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

import glob
import os
import pytest


def pytest_generate_tests(metafunc):
    """Replace the xmltestcases fixture by all *.case.xml files in tests/cases"""
    if "xmltestcase" in metafunc.fixturenames:
        location = os.path.dirname(os.path.realpath(__file__))
        testcases = glob.glob(location + "/cases/*.case.xml")
        testcases.sort()  # Sort them alphabetically
        metafunc.parametrize("xmltestcase", testcases)
