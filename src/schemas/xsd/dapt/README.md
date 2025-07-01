# DAPT XSD Readme

The [DAPT](https://www.w3.org/TR/dapt/) XML Schema is provided as an informative (i.e. non-normative) addition
to the specification as an aid to implementers.

The XML Schema is provided as an [XSD 1](https://www.w3.org/TR/xmlschema-1/) (XML Schema definition language) document.

## Usage

An XSD 1 conformant XML validator should be able to validate a DAPT document against the top level [`dapt.xsd`](dapt.xsd)
schema document.

Since part of the schema is pulled in via a git submodule,
either clone the repository recursively or manually ensure that the submodule is cloned
to your local machine.

As a convenience, a Python script is provided to allow use of the XSDs to validate
a DAPT document using only open source libraries. The script is in the `schema-validator` folder.

## Design

The DAPT XSD is designed to be inclusive of all content predicted from the DAPT specification,
rather than defining attributes and elements from the DAPT specification
and relying on external XSDs for other namespace vocabulary.
This also permits DAPT-specific constraints, such as the prohibition of the `<animation>` element,
or the requirement for the `daptm:scriptRepresents` attribute on the root `<tt>` element,
can be applied.

### Sources

Structurally, much of the XSD consists of a copy of the [TTML2 XSD](https://github.com/w3c/ttml2/tree/main/spec/xsd), though in some cases changes have been
made to represent those additional DAPT constraints.
This means that if the TTML2 XSD changes, there could be a maintenance task to update the DAPT XSD.
However it also simplifies usage.

Additionally, DAPT namespaces and DAPT-specific data types are defined in imported files whose name is prefixed `dapt-`.

EBU-TT Metadata is imported via a git submodule pointed at the XSD 1 version of the
[EBU-TT Metadata schema](https://github.com/ebu/ebu-tt-m-xsd/tree/issue-0030-schema-v1).

### Type restrictions

Two mechanisms are used to enforce DAPT-specific type restrictions:

1. DAPT-specific complex type definitions with `xs:complexContent` containing `xs:restriction` based on the TTML2 type.
This method is used where attributes permitted on the TTML2 type are prohibited in DAPT, and/or when additional
DAPT-specific attributes need to be permitted as extensions to the TTML2 element.
The relevant element definitions then point to the restricted DAPT type rather than the base TTML2 type.
2. Edits to remove DAPT-prohibited elements or attribute groups from TTML2 types - where this
pattern is used, XML comments highlight the change in the XSD file.

