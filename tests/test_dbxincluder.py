import os.path
import sys
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


def test_stdin(capsys):
    # Use relative paths to ensure the output looks always the same
    location = os.path.relpath(os.path.dirname(os.path.realpath(__file__)))
    stdin = sys.stdin  # Mock stdin
    sys.stdin = open(location + "/cases/basicxml.case.xml")
    outputxml = open(location + "/cases/basicxml.out.xml").read()
    ret = dbxincluder.main(["", "-"])
    sys.stdin.close()
    sys.stdin = stdin
    assert ret == 0
    assert capsys.readouterr()[0] == outputxml


def test_xml(xmltestcase):
    inputxml = open(xmltestcase, "rb").read()
    outputxml = open(xmltestcase[:-8] + "out.xml", "r").read()
    assert dbxincluder.process_xml(inputxml, os.path.relpath(os.path.dirname(xmltestcase)), xmltestcase) == outputxml
