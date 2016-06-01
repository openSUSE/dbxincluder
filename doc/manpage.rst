Manual Page for dbxincluder
===========================

SYNOPSIS
--------

::

  dbxincluder [options] [--] <input>
  dbxincluder -h | --help
  dbxincluder --version


DESCRIPTION
-----------

dbxincluder is an implementation of the XInclude 1.1 specification
(https://www.w3.org/TR/xinclude-11)
with support for DocBook transclusion (http://docbook.org/docs/transclusion).

If the input file is specified as "-", standard input is used.
The result is printed to standard output or the output file, if given.

OPTIONS
-------

-o <output>   Output file [default: -]
-c <catalog>  XML catalog to use [default: /etc/xml/catalog]
-h, --help    Print the version and help on usage.
--version     Show the version.

EXAMPLE
-------

dbxincluder input.xml > output.xml

BUGS
----

- Does not support XPointers and all attributes that provide references
