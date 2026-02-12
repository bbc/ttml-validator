.. SPDX-FileCopyrightText: © 2026 BBC
..
.. SPDX-License-Identifier: BSD-3-Clause

Testing
=======

The ``test`` package contains unit tests for all of the
pre-parsing checks and the XML checks, as well as for the
validation logging functionality.

Running the tests
-----------------

After installation you can run the tests:

Replacing ``$launchtool`` with ``poetry`` or ``uv`` according to your environment:

Unit tests
----------

::

    $launchtool run python -m unittest

Test coverage
-------------

To generate coverage data while testing:
::

    $launchtool run python -m coverage run -m unittest

To view the coverage report in the shell:
::

    $launchtool run python -m coverage report

To view the coverage report in a navigable HTML page:
::

    $launchtool run python -m coverage html

then open the resulting HTML file in your browser, e.g.

::

    open htmlcov/index.html
