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

"""xinclude module: Processes raw XInclude 1.1 elements"""

import os.path
import lxml.etree
import urllib.request


class DBXIException(Exception):
    """Exception type for XML errors"""
    def __init__(self, elem, message=None, file=None):
        """Construct an DBXIException
        :param elem: Element that caused error
        :param message: Message to show. Can be None.
        :param file: URL of source, can be None."""
        file = file if file is not None else ""
        message = ": " + message if message else ""
        self.error = "Error at {0}:{1}{2}".format(file, elem.sourceline, message)
        super().__init__(self.error)


def copy_attributes(elem, subtree):
    """Modifies subtree according to
    https://www.w3.org/XML/2012/08/xinclude-11/Overview.html#attribute-copying
    with the attributes of elem. Does not return anything.
    :param elem: XInclude source elemend
    :param subtree: Target subtree/element"""

    # Iterate all attributes
    for name, value in elem.items():
        if name == "set-xml-id":
            # Override/Remove xml:id on all top-level elements
            if len(value):
                subtree.set("{http://www.w3.org/XML/1998/namespace}id", value)
            elif subtree.get("{http://www.w3.org/XML/1998/namespace}id"):
                del subtree.attrib["{http://www.w3.org/XML/1998/namespace}id"]
        elif name.startswith("{http://www.w3.org/2001/XInclude/local-attributes}"):
            # Set attribute on all top-level elements
            subtree.set(name[len("{http://www.w3.org/2001/XInclude/local-attributes}"):], value)
        elif name.startswith("{http://www.w3.org/XML/1998/namespace}"):
            # Ignore xml: namespace
            continue
        elif name.startswith("{"):
            # Set attribute on all top-level elements
            subtree.set(name, value)


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


def handle_xinclude(elem, base_url, file=None, xinclude_stack=None):
    """Process the xi:include tag elem
    :param elem: The XInclude element to process
    :param base_url: xml:base to use if not specified in the document
    :param file: URL used to report errors
    :param xinclude_stack: List (or None) of str with url and fragid to detect infinite recursion"""
    assert elem.tag == "{http://www.w3.org/2001/XInclude}include", "Not an XInclude"
    assert elem.getparent() is not None, "XInclude without parent"

    # Get fragid
    fragid = elem.get("fragid")
    if elem.get("parse", "xml") != "xml" and fragid is not None:
        raise DBXIException(elem, "fragid invalid, parse != 'xml'", file)

    # Get base (nearest xml:base or current directory)
    base_urls = elem.xpath("ancestor-or-self::*[@xml:base][1]/@xml:base")

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

    # Check for infinite recursion
    if xinclude_stack is None:
        xinclude_stack = []

    xinclude_id = "{0!r}>{1!r}".format(url, fragid)
    if xinclude_id in xinclude_stack:
        raise DBXIException(elem, "Infinite recursion detected", file)

    # Parse as XML
    subtree = lxml.etree.fromstring(content)

    # Get subdocument
    if fragid is not None:
        subtree = subtree.xpath("//*[@xml:id={0!r}]".format(fragid))
        if len(subtree) == 1:
            subtree = subtree[0]
            # Get xml:base of subdocument
            base_urls = subtree.xpath("ancestor-or-self::*[@xml:base][1]/@xml:base")
            url = base_urls[0] if len(base_urls) == 1 else url
        else:
            raise DBXIException(elem, file=file,
                                message="Could not find fragid {0!r} in target {1!r}"
                                .format(fragid, url))

    # Copy certain attributes from xi:include to the target tree
    copy_attributes(elem, subtree)

    subtree.tail = saved_tail
    process_tree(subtree, url, url, xinclude_stack + [xinclude_id])

    # Replace XInclude by subtree
    elem.getparent().replace(elem, subtree)


def process_tree(tree, base_url=None, file=None, xinclude_stack=None):
    """Processes an ElementTree:
       - Search and process xi:include
       - Add xml:base (=source) to the root element
    :param tree: ElementTree to process
    :param base_url: xml:base to use if not set in the tree
    :param file: URL used to report errors
    :param xinclude_stack: Internal"""

    if base_url and not tree.get("{http://www.w3.org/XML/1998/namespace}base"):
        tree.set("{http://www.w3.org/XML/1998/namespace}base", base_url)

    for elem in tree.getiterator():
        if elem.tag == "{http://www.w3.org/2001/XInclude}include":
            handle_xinclude(elem, base_url, file, xinclude_stack)


def process_xml(xml, base_url=None, file=None):
    """Same as process_tree, but input and output is text"""
    if not isinstance(xml, bytes):
        xml = bytes(xml, encoding="UTF-8")

    tree = lxml.etree.fromstring(xml, base_url=base_url)

    process_tree(tree, base_url, file)

    return lxml.etree.tostring(tree.getroottree(), encoding='unicode',
                               pretty_print=True)
