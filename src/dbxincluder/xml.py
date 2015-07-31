#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

import sys
import py.path
from lxml import etree
from .core import NS


def getxmlparser(**kwargs):
    """Returns a XMLParser object

    :param dict kwargs: Dictionary which should contain the same keys
                        as in etree.XMLParser
                        Additionally:
                        'resolvers' (list): list of resolvers of type
                                            etree.Resolver
    :return: XMLParser object
    :rtype: lxml.etree.XMLParser
    """

    xmldict = dict( # These values are "our": # flake8: noqa
                   remove_blank_text=False,
                   resolve_entities=False,
                   load_dtd=False,
                   dtd_validation=False,
                   ns_clean=True,
                   # These are the default values:
                   encoding=None,
                   attribute_defaults=False,
                   no_network=True,
                   recover=False,
                   schema=None,
                   remove_comments=False,
                   remove_pis=False,
                   strip_cdata=True,
                   collect_ids=True,
                   target=None,
                   compact=True,
                   )

    # dictkeys = ('encoding',
    #            'attribute_defaults',
    #            'no_network',
    #            'recover',
    #            'schema',
    #            'remove_blank_text',
    #            'remove_comments',
    #            'remove_pis',
    #            'strip_cdata',
    #            'collect_ids',
    #            'target',
    #            'compact',
    #            )

    # Combine it with passed values from kwargs, but ignore any other
    # values
    for key, value in xmldict.items():
        xmldict[key] = kwargs.get(key, value)
    try:
        resolvers = kwargs.pop('resolvers')
    except KeyError:
        resolvers = []

    parser = etree.XMLParser(**xmldict)
    for resolver in resolvers:
        parser.resolver.add(resolver)
    return parser


def adjust_ids(tree):
    # TODO
    pass


def adjust_idrefs(tree):
    pass


def transclude_cleanup(tree):
    pass


def transclude(tree):
    pass


def xinclude(tree, parser):

    basedir = py.path.local(tree.docinfo.URL).dirname
    # print("****")
    for xi in tree.iterfind("//xi:include", namespaces=NS):
        href = xi.attrib.get('href')
        # print("---", href)
        if href is None:
            print("no href found", file=sys.stderr)
            sys.exit(100)
        href = basedir + "/" + href

        # print(xi, href, file=sys.stderr)
        xitree = etree.parse(str(href), parser)
        xi.getparent().replace(xi, xitree.getroot())
    return tree


def parsexml(source):
    """
    """
    parser = getxmlparser()
    tree = etree.parse(source, parser)

    tree = xinclude(tree, parser)
    print(etree.tostring(tree).decode("UTF-8"))
