<!--
SPDX-FileCopyrightText: © 2026 BBC

SPDX-License-Identifier: BSD-3-Clause
-->

# Security Policy

## Reporting a Vulnerability

Our full security policy and vulnerability reporting procedure is documented on [this external website](https://www.bbc.com/backstage/security-disclosure-policy/#reportingavulnerability).

Please note that this is a general BBC process. Communication will not be direct with the team responsible for this repo.

If you would like to, you can also open an issue in this repo regarding your disclosure, but please never share any details of the vulnerability in the GitHub issue.

## Dependency updates

This repository uses Dependabot to track updates to dependencies.
To reduce the potential for supply chain attacks,
a cooldown period of 7 days is specified for new versions of dependencies.
This means that, unless there are exceptional circumstances, we will not
update a dependency to a new release until that release is at least 7 days old.
