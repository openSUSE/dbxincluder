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

"""Main module"""

import sys
import lxml.etree

from . import docbook
from . import utils

__version__ = "0.1.0"


def main(argv=None):
    """Default entry point.
    Parses argv (sys.argv if None) and does stuff."""
    argv = argv if argv else sys.argv

    if len(argv) != 2 or "--help" in argv or "-h" in argv:
        # Print usage
        print("dbxincluder {0}".format(__version__))
        print("""Usage:
\tdbxincluder -h | --help\tPrint help
\tdbxincluder --version  \tPrint version
\tdbxincluder <xml file> \tProcess file and output to STDOUT
\tdbxincluder -          \tProcess STDIN and output to STDOUT""")
        return 2
    elif argv[1] == "--version":
        # Print version
        print("dbxincluder {0}".format(__version__))
        return 0

    base_url = None if argv[1] == "-" else argv[1]
    path = "<stdin>" if argv[1] == "-" else argv[1]

    try:
        file = sys.stdin if argv[1] == "-" else open(argv[1], "r")
        tree = lxml.etree.parse(file)
    except (lxml.etree.XMLSyntaxError, UnicodeDecodeError, IOError) as exc:
        sys.stderr.write("Could not parse {0!r}: {1}\n".format(path, str(exc)))
        return 1

    try:
        docbook.process_tree(tree.getroot(), base_url, path)
        sys.stdout.write(lxml.etree.tostring(tree, encoding='unicode',
                                             pretty_print=True))
    except utils.DBXIException as exc:
        sys.stderr.write(str(exc) + "\n")
        return 1

    return 0
