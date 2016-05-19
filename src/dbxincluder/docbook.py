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

"""Handle the DocBook specific part of transclusion"""

import lxml.etree

from lxml.etree import QName
from . import xinclude
from .utils import DBXIException, NS, QN, generate_id, get_inherited_attribute


def associate_new_ids(subtree):
    """Assign elements their new ids as new 'dbxi:newid' attribute.

    :param subtree: The XIncluded subtree to process"""
    idfixup = subtree.get(QName(NS['trans'], "idfixup"), "none")

    if idfixup not in ["none", "suffix", "auto"]:
        raise DBXIException(subtree, "Invalid value for idfixup: {0!r}. "
                            "Expected 'none', 'suffix' or 'auto'.".format(idfixup))

    if idfixup == "none":
        return  # Nothing to do here

    suffix = None
    if idfixup == "suffix":
        suffix, _ = get_inherited_attribute(subtree, "trans:suffix")
        if suffix is None:
            raise DBXIException(subtree, "no suffix found")

    for elem in subtree.iter():
        cur_id = elem.get(QN['xml:id'])
        if cur_id is None:
            continue

        new = elem.get(QN['dbxi:newid'], cur_id)
        if idfixup == "suffix":
            new = new + suffix
        elif idfixup == "auto":
            new = new + "--" + generate_id(elem)
        else:
            assert False, "This can't happen"  # pragma: no cover

        elem.set(QN['dbxi:newid'], new)


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
        assert False, "linkscope not handled"  # pragma: no cover

    return None if len(target) == 0 else target[0]


def new_ref(elem, idfixup_elem, value, linkscope):
    """Returns the fixed reference as string or None.
    Uses same parameters as find_target."""
    target = find_target(elem, idfixup_elem, value, linkscope)
    if target is None:
        return None

    new = target.get(QN['dbxi:newid'])
    if not new:
        new = target.get(QN['xml:id'])
        if not new:
            assert False, "Apparently find_target returned something weird."  # pragma: no cover

    return new


def fixup_references(subtree):
    """Fix all references if idfixup is set

    :param subtree: subtree to process"""

    for elem in subtree.iter():
        if not isinstance(elem.tag, str) or QName(elem).namespace != NS['db']:
            continue

        linkscope, _ = get_inherited_attribute(elem, "trans:linkscope", "near")

        if linkscope not in ["near", "local", "global", "user"]:
            raise DBXIException(elem, "invalid linkscope type {0!r}".format(linkscope))

        (idfixup, idfixup_elem) = get_inherited_attribute(elem, "trans:idfixup", "none")

        if idfixup == "none" or linkscope == "user":
            continue  # Nothing to do here

        idrefs = ["linkend", "otherterm", "startref", "targetptr", "endterm"]
        idrefs_multi = ["arearefs", "linkends", "zone"]

        for attr, value in elem.items():
            if attr not in idrefs and attr not in idrefs_multi:
                continue

            targets = [value]

            if attr in idrefs_multi:
                targets = value.split()

            new_targets = [new_ref(elem, idfixup_elem, t, linkscope) for t in targets]
            if None in new_targets:
                ref = targets[new_targets.index(None)]
                raise DBXIException(elem, "Could not resolve reference {0!r}".format(ref))

            elem.set(attr, " ".join(new_targets))


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
    fixup_references(tree)

    # Third, clean up our dbxi:newid and the docbook transclude attributes
    for elem in tree.iter():
        newid = elem.get(QN['dbxi:newid'])
        if newid:
            elem.set(QN['xml:id'], newid)
            del elem.attrib[QN['dbxi:newid']]

        for name, _ in elem.items():
            if QName(name).namespace == NS['trans']:
                del elem.attrib[name]

    # Remove unnecessary namespace declarations
    lxml.etree.cleanup_namespaces(tree)
