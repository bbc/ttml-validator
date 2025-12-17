Pre-parse Checks
================

The pre-parse checks allow issues that can affect XML parsing to be identified
and potentially fixed before an attempt is made to parse the document.

Character encoding issues
-------------------------

Both DAPT and the IMSC Text profiles of TTML require that the document is
encoded as UTF-8. Real world problems that we have observed include:

* the presence of null bytes
* the presence of byte sequences that are not legal in UTF-8
* the presence of byte sequences that are legal, but highly unlikely, that
  are symptomatic of encoding issues, such as "latin-1" encoded badly, in
  such a way that if the bytes were decoded as "utf-8" and then the
  result re-encoded as "latin-1" the result is actually the desired UTF-8
  byte sequence.
* strings encoded in some scheme that is not UTF-8, in some cases also
  claiming to be UTF-8.
* Byte Order Marks (BOMs) that were prepended to a string *before* encoding
  that string as UTF-8, thus corrupting the BOM.

Three checks are provided to look for these issues and resolve them:
* :py:class:`NullByteCheck<src.preParseChecks.preParseCheck.NullByteCheck>`
  looks for and removes null bytes;
* :py:class:`ByteOrderMarkCheck<src.preParseChecks.preParseCheck.ByteOrderMarkCheck>`
  looks for byte order marks and, if it finds it, removes a UTF-8 encoded
  UTF-8 BOM.
* :py:class:`BadEncodingCheck<src.preParseChecks.preParseCheck.BadEncodingCheck>`
  attempts to identify the encoding and, if it it not UTF-8, re-encodes
  the input as UTF-8 after decoding it using the most likely encoding found.

XML structure issues
--------------------

The :py:class:`XmlStructureCheck<src.preParseChecks.xmlStructureCheck.XmlStructureCheck>` checks for the presence of an XML document type declaration
and any entity declarations, as well as any non-UTF-8 document encoding claim.
If it finds any it logs the error and then continues. It does not modify the
input bytes, for example to replace the encoding declaration. This could
feasibly produce unexpected results if the XML parser attempts to decode the
contents as something other than UTF-8 after the ``BadEncodingCheck`` has
re-encoded the document as UTF-8.
