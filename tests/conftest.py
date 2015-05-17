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
# You should have received a copy of the GNU General Public License
# along with this program; if not, contact SUSE LLC.
#
# To contact SUSE about this file by physical or electronic mail,
# you may find current contact information at www.suse.com

import sys
import os

import pytest
import py.path
from lxml import etree

testdir = py.path.local(py.path.local(__file__).dirname)

# Add current directory; this makes it possible to import all
# docmanager related files
sys.path.append('.')

# ------------------------------------------------------
# Markers
#
reason = 'Fails on Travis or else there is no network connection to GitHub.'

travis = os.environ.get('TRAVIS', False)
skipif_travis = pytest.mark.skipif(travis, reason=reason)

no_network = os.environ.get('DM_NO_NETWORK_TESTS', False)
skipif_no_network = pytest.mark.skipif(no_network, reason=reason)

# ------------------------------------------------------
# Version Check
#
def compare_pytest_version(minimum):
    """Compares existing pytest version with required

    :param list minimum: Minimum version in the form of
                         [major, minor, release ]
    :return: condition met (True) or not (False)
    :rtype: bool
    """
    pytestversion = [ int(n) for n in pytest.__version__.split('.')]
    minimum = list(minimum)
    return minimum > pytestversion


# ------------------------------------------------------
# Fixtures
#

@pytest.fixture
def testdir():
    """Fixture: Returns the test directory"""
    return py.path.local(py.path.local(__file__).dirname) / "files"
