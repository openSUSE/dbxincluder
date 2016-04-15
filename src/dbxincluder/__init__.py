#
# Copyright (c) 2016 SUSE Linux GmbH
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#

"""Main module. Contains everything needed to transclude."""

import os.path
import sys
import lxml.etree
import urllib.request

__version__ = "0.0"


class DBXIException(Exception):
    """ Exception type for XML errors"""
    def __init__(self, elem, message=None, file=None):
        file = file if file is not None else ""
        message = ": " + message if message else ""
        self.error = "Error at {0}:{1}{2}".format(file, elem.sourceline, message)
        super().__init__(self.error)


def get_target(elem, base_url, file=None):
    """Return (the content of the target document as string, the URL that was used)
    :param elem: XInclude element
    :param base_url: xml:base of the element
    """
    # Get href
    href = elem.get("href")
    if href is None:
        raise DBXIException(elem, "Missing href attribute", file)

    # Build full URL
    url = "/".join(base_url.split("/")[:-1]) + "/" + href

    try:
        if "://" in base_url:
            target = urllib.request.urlopen(base_url)
        else:  # Add file:// for URLs without scheme
            target = urllib.request.urlopen("file://" + os.path.abspath(url))
        content = target.read()
        target.close()
    except urllib.error.URLError:
        raise DBXIException(elem, "Could not get target {0!r}".format(url), file)
    except IOError as ioex:
        raise DBXIException(elem, "Could not get target {0!r}: {1}".format(url, ioex), file)

    return content, url


def handle_xinclude(elem, base_url, file=None):
    """Process the xi:include tag elem"""
    assert elem.tag == "{http://www.w3.org/2001/XInclude}include", "Not an XInclude"
    assert elem.getparent() is not None, "XInclude without parent"

    # Get fragid
    fragid = elem.get("fragid")
    if elem.get("parse", "xml") != "xml" and fragid is not None:
        raise DBXIException(elem, "fragid invalid, parse != 'xml'", file)

    # Get base (nearest xml:base or current directory)
    base_urls = elem.xpath("ancestor-or-self::*[@xml:base][1]/@xml:base",
                           namespaces={'xml': "http://www.w3.org/XML/1998/namespace"})

    base_url = base_urls[0] if len(base_urls) == 1 else base_url
    if base_url is None:
        raise DBXIException(elem, "Could not get base URL", file)

    # Save text after element
    saved_tail = elem.tail
    elem.tail = ""

    # Load target
    content, url = get_target(elem, base_url, file)

    # Include as text
    if elem.get("parse", "xml") != "xml":
        prev = elem.getprevious()
        if prev is not None:
            prev.tail += str(content, encoding="utf-8") + saved_tail
        else:
            elem.getparent().text += str(content, encoding="utf-8") + saved_tail
        return

    # Parse as XML
    subtree = lxml.etree.fromstring(content)

    # Get subdocument
    if fragid is not None:
        subtree = subtree.xpath("//*[@xml:id={0!r}]".format(fragid),
                                namespaces={'xml': "http://www.w3.org/XML/1998/namespace"})
        if len(subtree) == 1:
            subtree = subtree[0]
            # Get xml:base of subdocument
            base_urls = subtree.xpath("ancestor-or-self::*[@xml:base][1]/@xml:base",
                                      namespaces={'xml': "http://www.w3.org/XML/1998/namespace"})
            url = base_urls[0] if len(base_urls) == 1 else url
        else:
            raise DBXIException(elem, "Could not find fragid {0!r} in target {1!r}".format(fragid, url), file)

    subtree.tail = saved_tail
    process_tree(subtree, url)

    # Replace XInclude by subtree
    elem.getparent().replace(elem, subtree)


def process_tree(tree, base_url=None, file=None):
    """Processes an ElementTree:
       - Search and process xi:include
       - Replace xml:id (TODO)
       - Add xml:base (=source) to the root element"""

    if base_url and not tree.get("{http://www.w3.org/XML/1998/namespace}base"):
        tree.set("{http://www.w3.org/XML/1998/namespace}base", base_url)

    for elem in tree.getiterator():
        if elem.tag == "{http://www.w3.org/2001/XInclude}include":
            handle_xinclude(elem, base_url, file)


def process_xml(xml, base_url=None, file=None):
    """Does nothing"""
    if not isinstance(xml, bytes):
        xml = bytes(xml, encoding="UTF-8")

    tree = lxml.etree.fromstring(xml, base_url=base_url)

    process_tree(tree, base_url, file)

    return lxml.etree.tostring(tree.getroottree(), encoding='unicode',
                               pretty_print=True)


def main(argv=None):
    """Default entry point.
    Parses argv (sys.argv if None) and does stuff."""
    argv = argv if argv else sys.argv

    if len(argv) != 2 or "--help" in argv:
        # Print usage
        print("dbxincluder {0}".format(__version__))
        print("""Usage:
\tdbxincluder --help    \tPrint help
\tdbxincluder --version \tPrint version
\tdbxincluder <xml file>\tProcess file and output to STDOUT
\tdbxincluder -         \tProcess STDIN and output to STDOUT""")
        return 2
    elif argv[1] == "--version":
        # Print version
        print("dbxincluder {0}".format(__version__))
        return 0

    base_url = None if argv[1] == "-" else argv[1]
    path = "<stdin>" if argv[1] == "-" else argv[1]
    try:
        file = sys.stdin if argv[1] == "-" else open(argv[1], "r")
        inputxml = file.read()
    except IOError as ioex:
        sys.stderr.write("Could not read {0!r}: {1}!\n".format(argv[1], ioex.strerror))
        return 1

    try:
        sys.stdout.write(process_xml(inputxml, base_url, path))
    except DBXIException as exc:
        sys.stderr.write(str(exc) + "\n")
        return 1

    return 0
