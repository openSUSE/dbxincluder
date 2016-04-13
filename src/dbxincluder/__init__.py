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


__version__ = "0.0"

import sys


def main(argv=None):
    """Default entry point.
    Parses argv (sys.argv if None) and does stuff."""
    if argv is None:
        argv = sys.argv

    if len(argv) != 2 or "--help" in argv:
        # Print usage
        print("dbxincluder {0}".format(__version__))
        print("""Usage:
              \tdbxincluder --help
              \tdbxincluder --version
              \tdbxincluder <xml file>""")
        return 2
    elif argv[1] == "--version":
        # Print version
        print("dbxincluder {0}".format(__version__))
        return 0
