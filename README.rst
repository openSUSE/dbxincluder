===========
dbxincluder
===========

Status: Planning

.. list-table::
    :stub-columns: 1

    * - tests
      - | |travis| 
        | |landscape| |scrutinizer|


.. |travis| image:: http://img.shields.io/travis/openSUSE/dbxincluder/develop.svg?style=flat&label=Travis
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/openSUSE/dbxincluder

..
    .. |appveyor| image:: https://img.shields.io/appveyor/ci/openSUSE/dbxincluder/master.svg?style=flat&label=AppVeyor
        :alt: AppVeyor Build Status
        :target: https://ci.appveyor.com/project/openSUSE/dbxincluder


.. |landscape| image:: https://landscape.io/github/openSUSE/dbxincluder/master/landscape.svg?style=flat
    :target: https://landscape.io/github/openSUSE/dbxincluder/master
    :alt: Code Quality Status

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/g/openSUSE/dbxincluder/develop.svg?style=flat
    :alt: Scrutinizer Status
    :target: https://scrutinizer-ci.com/g/openSUSE/dbxincluder/?branch=develop

Transclusions for DocBook with XInclude 1.1

http://docbook.org/docs/transclusion/


Installation
============

::

    pip install dbxincluder

Documentation
=============

.. 
    https://dbxincluder.readthedocs.org/

Development
===========

To run the all tests run::

    tox
