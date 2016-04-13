import pytest

import dbxincluder


def test_version(capsys):
    assert dbxincluder.main(["--version"]) == 0
    assert capsys.readouterr()[0] == "dbxincluder {0}\n".format(dbxincluder.__version__)


def test_help(capsys):
    assert dbxincluder.main(["--help"]) == 2
    capsys.readouterr()
