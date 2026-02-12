.. SPDX-FileCopyrightText: © 2026 BBC
..
.. SPDX-License-Identifier: BSD-3-Clause

XML (post-parsing) Checks
=========================

Assuming that parsing is successful, the validator creates an ``ElementTree``
object that represents the parsed XML document. It then iterates through the
list of :py:class:`XMLChecks<src.xmlChecks.xmlCheck.XmlCheck>`
supplied by the selected
:py:class:`ConstraintSet<src.constraintSets.constraintSet.ConstraintSet>`.

Each of these ``XMLCheck`` objects must be a derived class that implements
the :py:meth:`run<src.xmlChecks.xmlCheck.XmlCheck.run>` method,
stores any validation results and returns a boolean,
``True`` if the check passes, ``False`` otherwise.

``XMLCheck`` objects are _not_ supposed to modify the ``input``.
It may be that information can be derived during a check that is needed
for a later check. This can be stored in the ``context`` dictionary.
There is currently no dependency modelling to deal with checks that are
dependent on other checks having already run; in that scenario the check
should be written to proceed in some safe way, for example exiting
without completing the check and logging a :py:obj:`SKIP<src.validationLogging.validationResult.SKIP>`
:py:class:`ValidationResult<src.validationLogging.validationResult.ValidationResult>`.

There are a large number of checks, some of which traverse the element tree,
others that just check for a simple individual thing. Each derived
class should document itself. They live in the
:py:mod:`xmlChecks<src.xmlChecks>` module.
