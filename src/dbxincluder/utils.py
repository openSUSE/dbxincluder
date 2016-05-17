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


def generate_id(elem):
    """Generate a (per-document) unique ID for the XML element elem

    :return: str"""

    # If you change this algorithm, you need to regenerate all testcase outputs
    path = bytes(elem.getroottree().getpath(elem), encoding="utf-8")
    return str(base64.urlsafe_b64encode(path), encoding="utf-8").replace("=", "-")
