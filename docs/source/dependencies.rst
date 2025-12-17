Dependencies
============

ttml-validator uses as few dependencies as possible outside what is bundled
with Python.

.. todo::
    add url links to the dependencies


Encoding checks: ``charset-normalizer``
---------------------------------------

One of the issues we have frequently observed is incorrect encoding.
Since many workflows produce TTML documents whose content originated in
older binary formats such as STL, that use an 8 bit character set, the
toolchain needs to convert the character encoding into Unicode, and then
into UTF-8. Many tools do not do this properly, with results such as:

* Documents labelled as UTF-8 but actually contain character content
  encoded in some other character set
* Documents with an unexpected byte sequence at the beginning, such as
  a Byte Order Mark (BOM) that was prepended to a string representation
  of the documents and was *then* encoded as UTF-8
* Documents containing illegal byte sequences, or null bytes, that have
  no decoding in UTF-8

The ``charset-normalizer`` library provides a mechanism for identifying
the potential actual encodings of the document, and allowing it to be
queried.

XML Schema checks: ``xmlschema`` and XSDs
-----------------------------------------

A classical method for validating generic XML documents is to use a schema
and process the document against that schema, to see if it conforms.
Different schema languages exist; XML Schema Definition (XSD) documents
are available for TTML, IMSC, EBU-TT-D and DAPT.

The ``xmlschema`` library is able to parse an XSD and use it to validate an
XML document parsed as an ``ElementTree``.

Note that XML Schema validation alone is unable to check all potential
conformance requirements.

Two externally defined XSDs are copied into this repository:

* The DAPT XSD is from https://github.com/w3c/dapt/tree/main/xml-schemas 
  and includes the EBU-TT Metadata XSD from https://github.com/ebu/ebu-tt-m-xsd
* The EBU-TT-D XSD is from https://github.com/ebu/ebu-tt-xsd and similarly
  includes the EBU-TT Metadata XSD.

See the :py:mod:`schemas<src.schemas>` package.

Registries
----------

Where value sets are defined in a managed list, or a "registry",
the list is held in the code as a JSON file. In the case of DAPT,
those files are copied from the W3C specification repository at
https://github.com/w3c/dapt/tree/main/registries . In the case
of the TTML ``ttm:role`` registry, a JSON file has been synthesised
from the specification and equivalent wiki page at
https://www.w3.org/wiki/TTML/RoleRegistry .

See the :py:mod:`registries<src.registries>` package.

External test suites
--------------------

An external test suite for DAPT exists at https://github.com/w3c/dapt-tests
The DAPT validation code is tested against this suite, which is included
as a git submodule in the ``test`` package.

Development dependencies
------------------------

* Documentation: ``sphinx``.
* Test coverage: ``coverage``.
* Python documentation string validation: ``pydocstyle``.
* Python source code checking/linting: ``flake8``.
* Debug adaptor: ``debugpy``.

