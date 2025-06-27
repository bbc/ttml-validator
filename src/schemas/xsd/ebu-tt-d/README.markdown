# EBU-TT-D W3C XML Schema

The publication of the EBU-TT-D XML Schema for EBU-TT-D is intended to support the implementation of the specification in EBU-Tech 3380 version 1.0.

The current version of the EBU-TT-D XML Schema is 1.0.1.

Please note that the EBU-TT-D XML Schema is a helping document and NOT normative but informative.

To validate an XML document choose ebutt_d.xsd. This XML Schema file imports the other XSD's.

If you have any question regarding the use of the XML Schema please contact subtitling@ebu.ch or tai@irt.de.

## Contributors
Andreas Tai (IRT), Barbara Fichte (IRT), Gary Pearman, Nigel Megitt (BBC), Zoltan Kozma

## Acknowledgement
Parts of the EBU-TT-D W3C XML Schema were developed in the European collaborative research project HBB4ALL. This project has received funding from the European Union ICT Policy Support Programme (ICT PSP) under the Competitiveness and Innovation Framework Programme (CIP).

## RESOURCES     
EBU-TT-D SUBTITLING DISTRIBUTION FORMAT (EBU Tech 3380) https://tech.ebu.ch/publications/tech3380

## Copyright & license

Copyright (c) 2015, EBU-UER Technology & Innovation

The code is under BSD (3-Clause) License. (see LICENSE.txt)

## Cloning

This schema depends on the ebu/ebu-tt-m-xsd repository and imports it via a git submodule.

If cloning from the command line make sure to include the `--recurse-submodules` option,
or after cloning run `git submodule init` then `git submodule update`.
