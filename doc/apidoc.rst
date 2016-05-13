=============================
dbxincluder API documentation
=============================

Internals
=========

dbxincluder is divided into two parts.

The xinclude submodule handles the pure XInclude 1.1 specification.
It was necessary to re-implement it in python as libxml2 does not handle all necessary XInclude 1.1 features itself.

When processing a document, it is first run through the XInclude processor, then the DocBook transclusion processor.


dbxincluder.xinclude
====================

The XInclude process works in two stages.

The first stage handles all xi:include elements by replacing them with either the target subdocument
or the xi:fallback child, if available.

The second stage then handles the xi:fallback elements in the document by replacing them with their content.
As xi:fallback can contain muliple children, this can't happen in the first stage due to the way the iteration works.

.. automodule:: dbxincluder.xinclude
   :members:   

dbxincluder.docbook
===================

The DocBook transclusion process works in three stages.

First, the XIncluded document is iterated and each element with xml:id set gets a new custom dbxi:newid attribute.
This is computed for each element separately, based on the nearest trans:idfixup and trans:linkscope values.

The second stage iterates the document again, finding all references to elements in the same document and updating them
to the new values of the dbxi:newid attributes.

The last pass cleans up the custom attributes by setting xml:id to the value of dbxi:newid and removing the dbxi: attributes.
It also removes DocBook transclusiton attributes (trans:\*) and unneeded namespace declarations.

.. automodule:: dbxincluder.docbook
   :members:
