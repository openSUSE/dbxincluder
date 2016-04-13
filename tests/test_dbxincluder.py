import os
import pytest

import dbxincluder


def test_main(capsys):
    """runs __main__.py"""
    with pytest.raises(SystemExit):
        path = os.path.dirname(os.path.realpath(__file__)) + "/../src/dbxincluder/__main__.py"
        exec(compile(open(path).read(), path, "exec"), {}, {"__name__": "__main__"})


def test_version(capsys):
    assert dbxincluder.main(["", "--version"]) == 0
    assert capsys.readouterr()[0] == "dbxincluder {0}\n".format(dbxincluder.__version__)


def test_help(capsys):
    assert dbxincluder.main(["", "--help"]) == 2
    capsys.readouterr()


def test_xml(xmltestcase):
    input = open(xmltestcase).read()
    output = open(xmltestcase[:-8] + "out.xml").read()
    assert dbxincluder.process_xml(input) == output
