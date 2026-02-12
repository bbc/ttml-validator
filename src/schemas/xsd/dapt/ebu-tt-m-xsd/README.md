<!--
SPDX-FileCopyrightText: Copyright (C) 2019 EBU-UER Technology & Innovation

SPDX-License-Identifier: BSD-3-Clause
-->

## Current status: DRAFT, work in progress

Please consider this work as non-final for the time being.

## This repository

This repository contains an XML Schema for entities defined in the EBU-TT Metadata specification,
[Tech3390](https://tech.ebu.ch/publications/tech3390).

* Copyright 2019, EBU, www.ebu.ch
* Version of XML Schema: 0.9
* Creation: 24/05/2019

The publication of this EBU-TT XML Schema for EBU-TT Metadata is intended to support the 
implementation of the specification in EBU-Tech 3390 version 1.0.

Please note that the EBU-TT XML Schema is a helping document and NOT normative but informative.

## Style guide

Where an element is defined or referenced with either a `minOccurs` or a `maxOccurs`
that is not the default value (which is 1 for both), _both_ `minOccurs` and `maxOccurs`
should be explicitly specified.

The `use` attribute should only be specified when its value is `required` - in all other
cases the default `optional` value applies and does not need to be specified.
