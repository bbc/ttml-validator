Testing
=======

After installation you can run the tests:

Replacing ``$launchtool`` with ``poetry`` or ``uv`` according to your environment:

::

    $launchtool run python -m unittest

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
