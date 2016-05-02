import os.path
import sys
import pytest

import lxml.etree
import dbxincluder
import dbxincluder.xinclude
from dbxincluder.xinclude import DBXIException


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
    """Test whether it handles stdin correctly"""
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


def test_target():
    """Test dbxincluder.get_target"""
    # xi: namespace not looked at by get_target
    with pytest.raises(DBXIException):
        dbxincluder.xinclude.get_target(lxml.etree.fromstring("<xinclude href='nonexistant'/>"), os.path.curdir)
    with pytest.raises(DBXIException):
        dbxincluder.xinclude.get_target(lxml.etree.fromstring("<xinclude href='nonexistant'/>"), 'file://' + os.path.abspath(os.path.curdir) + "/")

    # Try to load this file
    quine = "<xinclude href={0!r}/>".format(os.path.relpath(__file__))
    assert dbxincluder.xinclude.get_target(lxml.etree.fromstring(quine), os.path.curdir+"/")[0] == open(__file__, "rb").read()


def test_xml(xmltestcase):
    """Runs one XML testcase"""
    inputxml = open(xmltestcase, "rb").read()
    filepart = xmltestcase[:-8]
    outputxml = open(filepart + "out.xml", "r").read() if os.path.isfile(filepart + "out.xml") else ""
    outputerr = open(filepart + "err.xml", "r").read() if os.path.isfile(filepart + "err.xml") else ""
    try:
        assert dbxincluder.process_xml(inputxml, os.path.relpath(xmltestcase), os.path.relpath(xmltestcase)) == outputxml
    except DBXIException as exc:
        assert str(exc) + "\n" == outputerr
