#
# Copyright (c) 2016 SUSE Linux GmbH
#
# This file is part of dbxincluder.
#
# dbxincluder is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# dbxincluder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dbxincluder. If not, see <http://www.gnu.org/licenses/>.

"""Utility functions and classes used throughout dbxincluder"""

import base64

from lxml.etree import QName


# Commonly used XML namespaces
NS = {'xml': "http://www.w3.org/XML/1998/namespace",
      'local': "http://www.w3.org/2001/XInclude/local-attributes",
      'xi': "http://www.w3.org/2001/XInclude",
      'trans': "http://docbook.org/ns/transclude",
      'db': "http://docbook.org/ns/docbook",
      # Custom namespace for temporary attributes
      'dbxi': "dbxincluder"}

# Commonly used attributes
QN = {'xml:id': QName(NS['xml'], "id"),
      'xml:base': QName(NS['xml'], "base"),
      'xi:include': QName(NS['xi'], "include"),
      'xi:fallback': QName(NS['xi'], "fallback"),
      'dbxi:newid': QName(NS['dbxi'], "newid")}


def get_inherited_attribute(elem, attribute, default=None):
    """Return the value of the inherited or directly set attribute or default.

    :param elem: The element to query
    :param attribute: The name of the attribute
    :return: Tuple of (str, None or default, element with value)"""

    values = elem.xpath("ancestor-or-self::*[@{0}][1]".format(attribute),
                        namespaces=NS)
    if len(values) == 0:
        return (default, None)

    return (values[0].xpath("@"+attribute, namespaces=NS)[0], values[0])


def create_xinclude_stack(elem):
    """Return a formatted string which prints the xml:base attributes in inverted order.
    Example:
    Included by source.xml
    Included by parent.xml

    :param elem: Source element
    :return str: Formatted string. Empty or starts with a newline"""
    xml_bases = elem.xpath("ancestor-or-self::*[@xml:base]/@xml:base", namespaces=NS)
    if len(xml_bases) < 2:
        return ""

    # We may get the original line here by adding a custom attribute in xinclude.process_xinclude
    return "\nIncluded by ".join([""] + xml_bases[:-1][::-1])


class DBXIException(Exception):
    """Exception type for XML errors"""
    def __init__(self, elem, message=None, file=None):
        """Construct an DBXIException.
        If file is none, it tries to get the file name by xml:base.
        Prints a "stack trace" of xml:base of elem.

        :param elem: Element that caused error
        :param message: Message to show. Can be None.
        :param file: URL of source, can be None."""

        # Try xml:base if no file provided
        if file is None or len(file) == 0:
            file = get_inherited_attribute(elem, "xml:base", "")[0]

        stack = create_xinclude_stack(elem)

        message = ": " + message if message else ""
        self.error = "Error at {0}:{1}{2}{3}".format(file, elem.sourceline, message, stack)
        super().__init__(self.error)


def generate_id(elem):
    """Generate a (per-document) unique ID for the XML element elem

    :return: str"""

    # If you change this algorithm, you need to regenerate all testcase outputs
    path = bytes(elem.getroottree().getpath(elem), encoding="utf-8")
    return str(base64.urlsafe_b64encode(path), encoding="utf-8").replace("=", "-")
