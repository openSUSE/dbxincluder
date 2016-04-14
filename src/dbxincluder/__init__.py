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
    pass


def handle_xinclude(elem, base_url):
    """Process the xi:include tag elem"""
    assert elem.tag == "{http://www.w3.org/2001/XInclude}include", "Not an XInclude"
    assert elem.getparent() is not None, "XInclude without parent"

    # Get href
    href = elem.get("href")
    if href is None:
        raise DBXIException("Missing href in {0}:{1}".format(base_url, elem.sourceline))

    # Get base (nearest xml:base or current directory)
    base_urls = elem.xpath("./ancestor-or-self::*[@xml:base][1]/@xml:base",
                           namespaces={'xml': "http://www.w3.org/XML/1998/namespace"})

    base_url = base_urls[0] if len(base_urls) == 1 else base_url
    if base_url is None:
        raise DBXIException("Could not get base URL for {0}:{1}".format(base_url, elem.sourceline))

    # Build full URL
    url = base_url + "/" + href

    try:
        target = urllib.request.urlopen(base_url)
    except ValueError:
        try:
            # Add file:// for URLs without scheme
            target = urllib.request.urlopen("file://" + os.path.abspath(url))
        except ValueError as exc:
            raise DBXIException("Could not get target for {0}:{1}: {2}".format(base_url, elem.sourceline, exc.args[0]))

    # Load, parse and process subtree
    subtree = lxml.etree.fromstring(target.read())
    process_tree(subtree, "/".join(url.split("/")[:-1]))

    # Replace XInclude by subtree
    elem.getparent().replace(elem, subtree)

def process_tree(tree, base_url=None):
    """Processes an ElementTree:
       - Search and process xi:include
       - Replace xml:id (TODO)
       - Add xml:base (=source) to the root element"""

    if base_url and not tree.get("{http://www.w3.org/XML/1998/namespace}base"):
        tree.set("{http://www.w3.org/XML/1998/namespace}base", base_url)

    for elem in tree.getiterator():
        if elem.tag == "{http://www.w3.org/2001/XInclude}include":
            handle_xinclude(elem, base_url)

    return tree


def process_xml(xml, base_url=None):
    """Does nothing"""
    if not isinstance(xml, bytes):
        xml = bytes(xml, encoding="UTF-8")

    tree = lxml.etree.fromstring(xml)

    tree = process_tree(tree, base_url)

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

    base_url = None if argv[1] == "-" else os.path.dirname(argv[1])
    try:
        file = sys.stdin if argv[1] == "-" else open(argv[1], "r")
        inputxml = file.read()
    except IOError as ioex:
        sys.stderr.write("Could not read {0!r}: {1}!\n".format(argv[1], ioex.strerror))
        return 1

    sys.stdout.write(process_xml(inputxml, base_url))
    return 0
