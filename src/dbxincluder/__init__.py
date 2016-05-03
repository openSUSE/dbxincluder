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

"""Main module. Handles the docbook specific part."""

import base64
import os.path
import sys
import lxml.etree

from . import xinclude
from .xinclude import DBXIException

__version__ = "0.0"


def generate_id(elem):
    """Generate a (per-document) unique ID for the XML element elem"""
    path = bytes(elem.getroottree().getpath(elem), encoding="utf-8")
    return str(base64.urlsafe_b64encode(path), encoding="utf-8")


def replace_id(subtree, old, new):
    """Replace all references to the ID old with new in subtree"""
    for elem in subtree.iter():
        if not elem.tag.startswith("{http://docbook.org/ns/docbook}"):
            continue

        idrefs = ["linkend", "linkends", "otherterm", "zone", "startref", "arearefs", "targetptr", "endterm"]
        idrefs_multi = ["arearefs", "linkends", "zone"]
        for attr, value in elem.items():
            if attr not in idrefs:
                continue

            if attr in idrefs_multi:
                assert False, "Not implemented"

            if elem.get(attr) == old:
                elem.set(attr, new)


def handle_idfixup(subtree, idfixup, linkscope, suffix):
    """Handle the docbook idfixup transclusion attribute"""
    if idfixup == "suffix":
        assert len(suffix), "No suffix given"

    for elem in subtree.iter():
        old = elem.get("{http://www.w3.org/XML/1998/namespace}id")
        if old is None:
            continue

        if idfixup == "suffix":
            new = old + suffix
            elem.set("{http://www.w3.org/XML/1998/namespace}id", new)
            replace_id(subtree, old, new)
        else:
            # TODO: Get file and line from somewhere
            raise DBXIException(elem, "idfixup type {0!r} not implemented".format(idfixup))


def process_docbook(elem):
    """Process attributes for docbook transclusion"""
    idfixup = elem.get("{http://docbook.org/ns/transclude}idfixup", "none")
    if idfixup == "none":
        return  # Nothing to do here

    linkscope = elem.get("{http://docbook.org/ns/transclude}linkscope", "near")
    suffix = elem.get("{http://docbook.org/ns/transclude}suffix")

    handle_idfixup(elem, idfixup, linkscope, suffix)

    # Remove transclusion attributes
    for name, value in elem.items():
        if name.startswith("{http://docbook.org/ns/transclude}"):
            del elem.attrib[name]


def process_xml(xml, base_url=None, file=None):
    """Same as xinclude.process_xml, but handle docbook attributes"""
    if not isinstance(xml, bytes):
        xml = bytes(xml, encoding="UTF-8")

    tree = lxml.etree.fromstring(xml, base_url=base_url)

    xinclude.process_tree(tree, base_url, file)
    for elem in tree.iter():
        process_docbook(elem)

    # Remove unnecessary namespace declarations
    lxml.etree.cleanup_namespaces(tree)

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
    except xinclude.DBXIException as exc:
        sys.stderr.write(str(exc) + "\n")
        return 1

    return 0
