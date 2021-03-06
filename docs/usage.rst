======================
How to use dbxincluder
======================

Installation
============

``dbxincluder`` depends on ``setuptools`` for automatic installation, ``docopt`` for option processing and
``lxml`` for XML processing.

Simply run:

.. code-block:: bash

  ./setup.py

to install ``dbxincluder``. A virtual Python3 environment (":command:`pyvenv`") is recommended.

Usage
=====

.. code-block:: bash

  > dbxincluder --help
  dbxincluder: XInclude and DocBook transclusion processor

  Usage:
    dbxincluder [options] [--] <input>
    dbxincluder -h | --help
    dbxincluder --version

  Options:
    -o <output>   Output file [default: -]
    -c <catalog>  XML catalog to use [default: /etc/xml/catalog]
    -h --help     Show this screen.
    --version     Show the version.

``dbxincluder`` either reads from standard input (stdin) or a file
and outputs to stdout or the given output file.
Error messages get printed to stderr.
The following invocations do the same:

.. code-block:: bash

  python3 -m dbxincluder input.xml
  dbxincluder input.xml
  dbxincluder - < input.xml
  dbxincluder -o - - < input.xml

Normally you want to write the output to a file.
Use redirection or the :option:`-o` option for that:

.. code-block:: bash

  python3 -m dbxincluder input.xml > output.xml
  dbxincluder input.xml > output.xml
  dbxincluder - < input.xml > output.xml
  dbxincluder -o output.xml - < input.xml
  dbxincluder -o output.xml input.xml


Example
=======

XInclude only
-------------

:file:`source.xml`:

.. code-block:: xml

  <?xml version="1.0" encoding="UTF-8"?>
  <root xmlns:xi="http://www.w3.org/2001/XInclude">
    <elem>ent1</elem>
    <another>
      <xi:include href="part.xml" />
    </another>
  </root>

:file:`part.xml`:

.. code-block:: xml

  <elem>ent2</elem>

Result:

.. code-block:: xml

  > dbxincluder source.xml 

  <root xml:base="source.xml">
    <elem>ent1</elem>
    <another>
      <elem xml:base="part.xml">ent2</elem>
    </another>
  </root>

DocBook Transclusion
--------------------

Example taken from http://docbook.org/docs/transclusion/#tutorial

:file:`source.xml`:

.. code-block:: xml

  <?xml version="1.0" encoding="UTF-8"?>
  <book xmlns="http://docbook.org/ns/docbook"
        xmlns:xi="http://www.w3.org/2001/XInclude"
        xmlns:trans="http://docbook.org/ns/transclude"
        version="5.0">
    <title>Definitive Printer Guide</title>
    <chapter xml:id="buy">
      <title>Buying printer</title>
      <para>Grab money, go to shop, ...</para>
    </chapter>
    <chapter>
      <title>Quick installation guide</title>
      <para>Carefully follow all procedures below.</para>
      <xi:include href="procedure.001.xml" trans:idfixup="auto"/>
    </chapter>
    <chapter>
      <title>Maintenance</title>
      <para>Be friendly to your printer when you speak to it.</para>
      <para>If the green led is blinking, please add missing paper using the following procedure.</para>
      <xi:include href="procedure.001.xml" trans:idfixup="auto"/>
    </chapter>
  </book>

:file:`procedure.001.xml`:

.. code-block:: xml

  <?xml version="1.0" encoding="UTF-8"?>
  <procedure xmlns="http://docbook.org/ns/docbook" xml:id="paper-insert">
    <title>Inserting paper into printer</title>
    <para>This procedure is for printer owners.
      If you don't have a printer, consider <link linkend="buy">buying one</link>.</para>  
    <step xml:id="s1"><para>Make sure that you have paper.</para></step>
    <step><para>Insert paper into printer. If you don't have paper, consult <xref linkend="s1"/></para></step>
  </procedure>

Result:

.. code-block:: xml

  > dbxincluder source.xml

  <book xmlns="http://docbook.org/ns/docbook" version="5.0" xml:base="source.xml">
    <title>Definitive Printer Guide</title>
    <chapter xml:id="buy">
      <title>Buying printer</title>
      <para>Grab money, go to shop, ...</para>
    </chapter>
    <chapter>
      <title>Quick installation guide</title>
      <para>Carefully follow all procedures below.</para>
      <procedure xml:id="paper-insert--LyovKlszXS8qWzNd" xml:base="procedure.001.xml">
    <title>Inserting paper into printer</title>
    <para>This procedure is for printer owners.
      If you don't have a printer, consider <link linkend="buy">buying one</link>.</para>  
    <step xml:id="s1--LyovKlszXS8qWzNdLypbM10-"><para>Make sure that you have paper.</para></step>
    <step><para>Insert paper into printer. If you don't have paper, consult <xref linkend="s1--LyovKlszXS8qWzNdLypbM10-"/></para></step>
  </procedure>
    </chapter>
    <chapter>
      <title>Maintenance</title>
      <para>Be friendly to your printer when you speak to it.</para>
      <para>If the green led is blinking, please add missing paper using the following procedure.</para>
      <procedure xml:id="paper-insert--LyovKls0XS8qWzRd" xml:base="procedure.001.xml">
    <title>Inserting paper into printer</title>
    <para>This procedure is for printer owners.
      If you don't have a printer, consider <link linkend="buy">buying one</link>.</para>  
    <step xml:id="s1--LyovKls0XS8qWzRdLypbM10-"><para>Make sure that you have paper.</para></step>
    <step><para>Insert paper into printer. If you don't have paper, consult <xref linkend="s1--LyovKls0XS8qWzRdLypbM10-"/></para></step>
  </procedure>
    </chapter>
  </book>
