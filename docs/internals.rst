.. SPDX-FileCopyrightText: © 2026 BBC
..
.. SPDX-License-Identifier: BSD-3-Clause

How ttml-validator works internally
===================================

Desired characteristics of the validator
----------------------------------------

Key goals for the ttml-validator include:

* Be as exhaustive as possible in finding issues, i.e. do not stop at the
  first problem found.
* Log all the faults found, and where checks were completed without problem,
  log success too.
* Allow for onward processing of the results so that patterns across large
  datasets can be identified.
* Be as permissive as possible in the input, and attempt to derive the likely
  intent, and document that, before moving on.
* Be extensible to accommodate new document types.
* Check for potential TTML errors that are suggested or implied but not
  explicitly defined, for example IDREFS attributes referencing
  elements for which no behaviour is defined.

Validation algorithm
--------------------

For validation run the validator does:

1. Load an appropriate :py:class:`constraintSet<src.constraintSets.constraintSet.ConstraintSet>` for the type of 
   document being validated. This contains a list of pre-parsing checks and a list of post-XML-parsing checks
   that will be used later, as well as a method for summarising the results.
2. Initiate a :py:class:`validationLogger<src.validationLogging.validationLogger.ValidationLogger>`
   to capture the results of the validation run.
3. Initiate a ``context`` dictionary to allow checks to pass information down the line.
4. Load the input bytes.
5. Iterate through the :py:class:`preParseChecks<src.preParseChecks.preParseCheck.PreParseCheck>` in the constraint set,
   running each against those bytes. This process can modify the input bytes prior to
   passing it forward to the next check, for example to ensure that it has
   the expected encoding, or to strip out illegal bytes.
6. Attempt to parse the processed byte stream as an XML document, using
   the Python ``ElementTree`` library. This approach is generic for all XML
   documents, as opposed to using a bindings-based approach which generally
   stops immediately if the input document cannot be mapped to the binding.
7. Iterate through the :py:class:`xmlChecks<src.xmlChecks.xmlCheck.XmlCheck>` in the constraint set,
   running each against the parsed document objects. These checks typically do
   not modify the input element tree.
8. Write out the validation log to the output file.
9. Summarise the overall document validity using the ``constraintSet``.
10. Exit with an appropriate code representing whether the document was valid
    or not.

Supported profiles of TTML
--------------------------

The ttml-validator currently validates two profiles of TTML2_:

* EBU-TT-D_ and `IMSC Text`_ profile, including constraints of the
  `BBC Subtitle Guidelines`_
* The DAPT_ profile of TTML2_.

.. _TTML2: https://www.w3.org/TR/ttml2/
.. _EBU-TT-D: https://tech.ebu.ch/publications/tech3380
.. _IMSC Text: https://www.w3.org/TR/ttml-imsc1.3/
.. _BBC Subtitle Guidelines: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/
.. _DAPT: https://www.w3.org/TR/dapt/
