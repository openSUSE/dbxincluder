Manual Page for dbxincluder
===========================

SYNOPSIS
--------

::

  dbxincluder [--] <input>
  dbxincluder -h | --help
  dbxincluder --version

DESCRIPTION
-----------

dbxincluder is an implementation of the XInclude 1.1 specification
(https://www.w3.org/TR/xinclude-11)
with support for DocBook transclusion (http://docbook.org/docs/transclusion).

If the input file is specified as "-", standard input is used.
The result is always printed to standard output.

OPTIONS
-------

-h, --help  Display help and usage information
--version   Show the program's version

EXAMPLE
-------

dbxincluder input.xml > output.xml

BUGS
----

- Does not support XPointers and all attributes that provide references
