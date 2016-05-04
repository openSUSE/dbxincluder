======================
How to use dbxincluder
======================

Installation
============

There are no requirements other than setuptools for automatic installation
and lxml for XML parsing and output.

Simply run 

::

  ./setup.py

to install dbxincluder. A virtual python3 environment ("pyvenv") is recommended.

Usage
=====

dbxincluder either reads from standard input (stdin) or a file
and always outputs to stdout. Error messages get printed to stderr.
The following invocations do the same:

::

  python3 -m dbxincluder input.xml
  dbxincluder input.xml
  dbxincluder < input.xml

Normally you want to write the output to a file.
Use redirection for that:

::

  python3 -m dbxincluder input.xml > output.xml
  dbxincluder input.xml > output.xml
  dbxincluder < input.xml > output.xml
