Validation Logging
==================

The validation logging framework superficially mimics Python's ``logging``
framework, however instead of formatting and outputting validation logging 
messages as soon as they are generated, they are stored in an object that
provides ``list`` functionality, the ability to collate repeated results,
and to serialise itself as plain text, CSV or JSON.

The :py:class:`ValidationLogger<src.validationLogging.validationLogger.ValidationLogger>` is a list of :py:class:`ValidationResult<src.validationLogging.validationResult.ValidationResult>` objects.

Each ``ValidationResult`` has:

* A status, being ``GOOD``, ``INFO``, ``WARN``, ``ERROR`` or ``SKIP``
* A code reflecting what it relates to - these are an ``enum`` at
  :py:class:`ValidationCode<src.validationLogging.validationCodes.ValidationCode>`
* A location ``str`` to identify where in the document the result applies
* A message ``str`` to describe in more detail the result of the check

To decide whether or not the validation passed or failed a relevant
subset of checks, the
:py:mod:`ValidationPassChecker<src.validationLogging.validationSummariser>`
module offers "pass checkers" that include
appropriate check codes, for example the
:py:class:`XmlPassChecker<src.validationLogging.validationSummariser.XmlPassChecker>` has a ``_check_codes``
list that contains all the appropriate ``ValidationCode`` values
for which check failures would indicate that the input is not
valid XML, whereas the
:py:class:`TtmlPassChecker<src.validationLogging.validationSummariser.TtmlPassChecker>` has TTML-specific check failures.

Typically a :py:class:`ConstraintSet<src.constraintSets.constraintSet.ConstraintSet>`
would check each appropriate ``ValidationPassChecker`` that is
relevant for its purpose, in its static
:py:meth:`summarise<src.constraintSets.constraintSet.ConstraintSet.summarise>` method, so that the results can be used to establish
where the error lies, for example the input document might be valid
XML but contain TTML errors.