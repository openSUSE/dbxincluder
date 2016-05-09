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

"""Handle the docbook specific part of transclusion"""

import lxml.etree

from . import xinclude
from .utils import DBXIException
from .utils import generate_id


def associate_new_ids(subtree):
    """Assign elements their new ids as new attribute

    :param subtree: The XIncluded subtree to process"""
    idfixup = subtree.get("{http://docbook.org/ns/transclude}idfixup", "none")
    if idfixup == "none":
        return  # Nothing to do here

    suffix = subtree.get("{http://docbook.org/ns/transclude}suffix")

    if idfixup == "suffix":
        assert len(suffix), "No suffix given"

    for elem in subtree.iter():
        old = elem.get("{http://www.w3.org/XML/1998/namespace}id")
        if old is None:
            continue

        new = elem.get("{dbxincluder}newid", old)
        if idfixup == "suffix":
            new = old + suffix
        elif idfixup == "auto":
            new = old + "--" + generate_id(elem)
        else:
            raise DBXIException(elem, "idfixup type {0!r} not implemented".format(idfixup))

        elem.set("{dbxincluder}newid", new)


def find_target(elem, subtree, value, linkscope):
    """Resolves reference to id value beginning from elem

    :param elem: Source of reference
    :param subtree: XIncluded subtree
    :param value: ID of reference
    :param linkscope: DB transclusion linkscope (local/near/global)
    :return: Target element or None"""
    if linkscope == "local":
        target = subtree.xpath("./*[@xml:id={0!r}]".format(value))
    elif linkscope == "near":
        while elem.getparent() is not None:
            elem = elem.getparent()
            target = elem.xpath("./*[@xml:id={0!r}]".format(value))
            if len(target):
                return target[0]
    elif linkscope == "global":
        target = elem.xpath("//*[@xml:id={0!r}]".format(value))
    else:
        raise DBXIException(elem, "linkscope type {0!r} not implemented".format(linkscope))

    return None if len(target) == 0 else target[0]


def fixup_references(subtree):
    """Fix all references if idfixup is set

    :param subtree: subtree to process"""
    idfixup = subtree.get("{http://docbook.org/ns/transclude}idfixup", "none")
    if idfixup == "none":
        return  # Nothing to do here

    linkscope = subtree.get("{http://docbook.org/ns/transclude}linkscope", "near")
    if linkscope == "user":
        return  # Nothing to do here

    for elem in subtree.iter():
        if not elem.tag.startswith("{http://docbook.org/ns/docbook}"):
            continue

        idrefs = ["linkend", "linkends", "otherterm", "zone", "startref",
                  "arearefs", "targetptr", "endterm"]
        idrefs_multi = ["arearefs", "linkends", "zone"]
        for attr, value in elem.items():
            if attr not in idrefs:
                continue

            if attr in idrefs_multi:
                assert False, "Not implemented"

            # Find referenced element
            target = find_target(elem, subtree, value, linkscope)

            if target is None:
                raise DBXIException(elem, "Could not resolve reference {0!r}".format(value))

            # Update reference
            new = target.get("{dbxincluder}newid")
            if not new:
                new = target.get("{http://www.w3.org/XML/1998/namespace}id")

            elem.set(attr, new)


def process_tree(tree, base_url, file):
    """Processes an ElementTree.
    Handles all xi:include with xinclude.process_tree
    and processes all docbook attributes on the output.

    :param tree: ElementTree to process (gets modified)
    :param base_url: xml:base to use if not set in the tree
    :param file: URL used to report errors
    :return: Nothing"""

    # Do XInclude processing first
    xinclude.process_tree(tree, base_url, file)

    # Three passes:
    # First, assign all elements a new ID
    for subtree in tree.iter():
        associate_new_ids(subtree)

    # Second, fixup all references
    for subtree in tree.iter():
        fixup_references(subtree)

    # Third, clean up our {dbxincluder} and the docbook transclude attributes
    for elem in tree.iter():
        newid = elem.get("{dbxincluder}newid")
        if newid:
            elem.set("{http://www.w3.org/XML/1998/namespace}id", newid)
            del elem.attrib["{dbxincluder}newid"]

        for name, _ in elem.items():
            if name.startswith("{http://docbook.org/ns/transclude}"):
                del elem.attrib[name]

    # Remove unnecessary namespace declarations
    lxml.etree.cleanup_namespaces(tree)


def process_xml(xml, base_url=None, file=None):
    """Same as process_tree, but input and output is text

    :param xml: str or UTF-8 encoded bytes of the input document
    :param base_url: xml:base to use if not set in the tree
    :param file: URL used to report errors
    :return: UTF-8 encoded bytes of the output document"""
    if not isinstance(xml, bytes):
        xml = bytes(xml, encoding="UTF-8")

    tree = lxml.etree.fromstring(xml, base_url=base_url)

    process_tree(tree, base_url, file)

    return lxml.etree.tostring(tree.getroottree(), encoding='unicode',
                               pretty_print=True)
