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

"""
dbxincluder: XInclude and DocBook transclusion processor

Usage:
  dbxincluder [--] <input>
  dbxincluder -h | --help
  dbxincluder --version

Options:
  -h --help     Show this screen.
  --version     Show the version.

"""

import docopt
import sys
import lxml.etree

from . import docbook
from . import utils

__version__ = "0.1.0"


def main(argv=None):
    """Default entry point.
    Parses argv (sys.argv if None) and does stuff."""
    argv = argv if argv else sys.argv

    try:
        opts = docopt.docopt(__doc__, argv[1:], help=True, version="dbxincluder " + __version__)
    except SystemExit as exc:
        sys.stderr.write(str(exc) + "\n")
        return 0 if exc.code is None else 1

    use_stdin = opts["<input>"] == "-"
    base_url = None if use_stdin else opts["<input>"]
    path = "<stdin>" if use_stdin else opts["<input>"]

    try:
        file = sys.stdin if use_stdin else open(base_url, "r")
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
