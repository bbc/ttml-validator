.. SPDX-FileCopyrightText: © 2026 BBC
..
.. SPDX-License-Identifier: BSD-3-Clause

Development
===========

Contribution requirements
-------------------------

Please see `CONTRIBUTING.md`_

Code of conduct
---------------

Please see `CODE_OF_CONDUCT.md`_

Code hygiene
------------

The CI environment will use ty to do static type checking, ruff for linting
and reuse for copyright and license checking. It's probably worth setting up
your development environment to use ty and ruff as you go so that your
code passes first time.

The configuration for ty and ruff is in pyproject.toml

We measure test coverage: if you add new code make sure there are unit tests
present for it too, as far as is possible.


.. _CONTRIBUTING.md: https://github.com/bbc/ttml-validator/blob/main/CONTRIBUTING.md
.. _CODE_OF_CONDUCT.md: https://github.com/bbc/ttml-validator/blob/main/CODE_OF_CONDUCT.md
