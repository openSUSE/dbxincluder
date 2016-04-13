import glob
import os
import pytest


def pytest_generate_tests(metafunc):
    """Replace the xmltestcases fixture by all *.case.xml files in tests/cases"""
    if 'xmltestcase' in metafunc.fixturenames:
        location = os.path.dirname(os.path.realpath(__file__))
        testcases = glob.glob(location + "/cases/*.case.xml")
        testcases.sort()  # Sort them alphabetically
        metafunc.parametrize("xmltestcase", testcases)
