#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#

"""XInclude 1.1 transcluder
"""

from core import __version__


def _parser():
    import argparse
    parser = argparse.ArgumentParser(prog="foo",
                                     description=__doc__
                                     )

    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + __version__
                        )

    parser.add_argument("files",
                        help="One or more DocBook XML files."
                        )

    parser.add_argument('-v', '--verbose',
                        action='count',
                        help="Increase verbosity level"
                        )
    return parser.parse_args()

def main():
    return _parser()