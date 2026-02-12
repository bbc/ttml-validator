# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

import unittest
from src.xmlChecks.xmlCheck import XmlCheck
from src.xmlChecks.xsdValidator import xsdValidator
from src.schemas.ebuttdSchema import EBUTTDSchema
from src.schemas.daptSchema import DAPTSchema
import xml.etree.ElementTree as ElementTree
from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationResult import ValidationResult, \
  ERROR, GOOD


class testXmlCheck(unittest.TestCase):
    maxDiff = None

    def test_no_direct_instantiation(self):
        not_impl_XmlCheck = XmlCheck()
        good_input_xml = """<?xml version="1.0" encoding="UTF-8"?><tt/>"""
        good_input_etree = ElementTree.fromstring(good_input_xml)
        vr = ValidationLogger()
        context = {}

        with self.assertRaises(NotImplementedError):
            not_impl_XmlCheck.run(
                input=good_input_etree,
                context=context,
                validation_results=vr)

    def test_xsdValidator_good_input_ebuttd(self):
        xsd_validator = xsdValidator(
            xml_schema=EBUTTDSchema,
            schema_name='EBU-TT-D')
        good_input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt:tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:tt="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ebuttm="urn:ebu:tt:metadata"
    xmlns:ebutts="urn:ebu:tt:style"
    ttp:cellResolution="32 15" ttp:timeBase="media">
  <tt:head>
    <tt:metadata>
      <ebuttm:documentMetadata>
        <ebuttm:conformsToStandard>urn:ebu:tt:distribution:2014-01</ebuttm:conformsToStandard>
        <ebuttm:conformsToStandard>http://www.w3.org/ns/ttml/profile/imsc1/text</ebuttm:conformsToStandard>
        <ebuttm:authoredFrameRate>60</ebuttm:authoredFrameRate>
        <ebuttm:authoredFrameRateMultiplier>1 1</ebuttm:authoredFrameRateMultiplier>
        <ebuttm:documentEbuttVersion>v1.0</ebuttm:documentEbuttVersion>
        <ebuttm:documentIdentifier>-1</ebuttm:documentIdentifier>
        <ebuttm:documentTargetAspectRatio>16:9</ebuttm:documentTargetAspectRatio>
        <ebuttm:documentCreationDate>2020-05-28</ebuttm:documentCreationDate>
        <ebuttm:documentRevisionDate>2020-05-28</ebuttm:documentRevisionDate>
        <ebuttm:documentRevisionNumber>1</ebuttm:documentRevisionNumber>
        <ebuttm:documentCountryOfOrigin>GBR</ebuttm:documentCountryOfOrigin>
      </ebuttm:documentMetadata>
    </tt:metadata>
    <tt:styling>
      <tt:style xml:id="defaultStyle" tts:textDecoration="none" tts:fontWeight="normal" tts:fontStyle="normal" tts:backgroundColor="#00000000" tts:color="#FFFFFF" tts:textAlign="center" tts:fontFamily="proportionalSansSerif" tts:fontSize="100%" tts:lineHeight="normal"/>
      <tt:style xml:id="textCenter" tts:textAlign="center" ebutts:linePadding="0.5c"/>
      <tt:style xml:id="textWhiteOnBlack" tts:color="#FFFFFF" tts:backgroundColor="#000000"/>
    </tt:styling>
    <tt:layout>
      <tt:region xml:id="bottom" tts:displayAlign="after" tts:padding="0%" tts:writingMode="lrtb" tts:origin="14.375% 10%" tts:extent="71.25% 80%"/>
      <tt:region xml:id="top" tts:displayAlign="before" tts:padding="0%" tts:writingMode="lrtb" tts:origin="14.375% 10%" tts:extent="71.25% 80%"/>
      <tt:region xml:id="vcenter" tts:displayAlign="center" tts:padding="0%" tts:writingMode="lrtb" tts:origin="14.375% 10%" tts:extent="71.25% 80%"/>
    </tt:layout>
  </tt:head>
  <tt:body>
    <tt:div style="defaultStyle">
      <tt:p xml:id="sub1" begin="00:00:00.07" end="00:00:01.32" region="bottom" style="textCenter"><tt:span style="textWhiteOnBlack">Subtitle one</tt:span></tt:p>
      <tt:p xml:id="sub2" begin="00:00:01.33" end="00:00:04.17" region="bottom" style="textCenter"><tt:span style="textWhiteOnBlack">Subtitle two line one</tt:span><tt:br/><tt:span style="textWhiteOnBlack">Subtitle two line two,</tt:span></tt:p>
      <tt:p xml:id="sub3" begin="00:00:04.18" end="00:00:06.92" region="bottom" style="textCenter"><tt:span style="textWhiteOnBlack">Subtitle three</tt:span></tt:p>
      <tt:p xml:id="sub4" begin="00:00:06.93" end="00:00:09.92" region="bottom" style="textCenter"><tt:span style="textWhiteOnBlack">Subtitle four line one,</tt:span><tt:br/><tt:span style="textWhiteOnBlack">subtitle four line two.</tt:span></tt:p>
      <tt:p xml:id="sub5" begin="00:00:09.95" end="00:00:14.38" region="bottom" style="textCenter"><tt:span style="textWhiteOnBlack">Subtitle five line one,</tt:span><tt:br/><tt:span style="textWhiteOnBlack">subtitle five line one</tt:span></tt:p>
      <tt:p xml:id="sub6" begin="00:00:14.40" end="00:00:18.05" region="bottom" style="textCenter"><tt:span style="textWhiteOnBlack">Subtitle six line one</tt:span><tt:br/><tt:span style="textWhiteOnBlack">subtitle six line two.</tt:span></tt:p>
    </tt:div>
  </tt:body>
</tt:tt>
"""
        good_input_etree = ElementTree.fromstring(good_input_xml)
        vr = ValidationLogger()
        context = {}
        valid = xsd_validator.run(
            input=good_input_etree,
            context=context,
            validation_results=vr)
        self.assertTrue(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=GOOD,
                location='Parsed document',
                message='EBU-TT-D XSD Validation passes',
                code=ValidationCode.xml_xsd
            )
        ])

    def test_xsdValidator_bad_input_ebuttd(self):
        xsd_validator = xsdValidator(
            xml_schema=EBUTTDSchema,
            schema_name='EBU-TT-D'
        )
        bad_input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt:tt xml:lang="en-GB" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling" xmlns:ttp="http://www.w3.org/ns/ttml#parameter" xmlns:tt="http://www.w3.org/ns/ttml" xmlns:ttm="http://www.w3.org/ns/ttml#metadata" xmlns:ebuttm="urn:ebu:tt:metadata" xmlns:ebutts="urn:ebu:tt:style" ttp:cellResolution="32 15" ttp:timeBase="media">
  <tt:head>
    <tt:metadata>
      <ebuttm:documentMetadata>
        <ebuttm:conformsToStandard>urn:ebu:tt:distribution:2014-01</ebuttm:conformsToStandard>
        <ebuttm:conformsToStandard>http://www.w3.org/ns/ttml/profile/imsc1/text</ebuttm:conformsToStandard>
        <ebuttm:authoredFrameRate>60</ebuttm:authoredFrameRate>
        <ebuttm:authoredFrameRateMultiplier>1 1</ebuttm:authoredFrameRateMultiplier>
        <ebuttm:documentEbuttVersion>v1.0</ebuttm:documentEbuttVersion>
        <ebuttm:documentIdentifier>-1</ebuttm:documentIdentifier>
        <ebuttm:documentTargetAspectRatio>16:9</ebuttm:documentTargetAspectRatio>
        <ebuttm:documentCreationDate>2020-05-28</ebuttm:documentCreationDate>
        <ebuttm:documentRevisionDate>2020-05-28</ebuttm:documentRevisionDate>
        <ebuttm:documentRevisionNumber>1</ebuttm:documentRevisionNumber>
        <ebuttm:documentCountryOfOrigin>GBR</ebuttm:documentCountryOfOrigin>
      </ebuttm:documentMetadata>
    </tt:metadata>
    <tt:styling>
      <tt:style xml:id="defaultStyle" tts:textDecoration="none" tts:fontWeight="normal" tts:fontStyle="normal" tts:backgroundColor="#00000000" tts:color="#FFFFFF" tts:textAlign="center" tts:fontFamily="proportionalSansSerif" tts:fontSize="100%" tts:lineHeight="normal"/>
      <tt:style xml:id="textCenter" tts:textAlign="center" ebutts:linePadding="0.5c"/>
      <tt:style xml:id="textWhiteOnBlack" tts:color="#FFFFFF" tts:backgroundColor="#000000"/>
    </tt:styling>
    <tt:layout>
      <tt:region xml:id="bottom" tts:displayAlign="after" tts:padding="0%" tts:writingMode="lrtb" tts:origin="14.375% 10%" tts:extent="71.25% 80%"/>
      <tt:region xml:id="top" tts:displayAlign="before" tts:padding="0%" tts:writingMode="lrtb" tts:origin="14.375% 10%" tts:extent="71.25% 80%"/>
      <tt:region xml:id="vcenter" tts:displayAlign="center" tts:padding="0%" tts:writingMode="lrtb" tts:origin="14.375% 10%" tts:extent="71.25% 80%"/>
    </tt:layout>
  </tt:head>
  <tt:body>
    <tt:div style="defaultStyle">
      <tt:p xml:id="sub1" begin="00:00:00.07" end="00:00:01.32" region="bottom" style="textCenter"><tt:span style="textWhiteOnBlack" tts:color="lime">Subtitle one</tt:span></tt:p>
      <tt:p xml:id="sub2" begin="00:00:01.33" end="00:00:04.17" region="bottom" style="textCenter"><tt:span style="textWhiteOnBlack">Subtitle two line one</tt:span><tt:br/><tt:span style="textWhiteOnBlack">Subtitle two line two,</tt:span></tt:p>
      <tt:p xml:id="sub3" begin="00:00:04.18" end="00:00:06.92" region="bottom" style="textCenter"><tt:span style="textWhiteOnBlack">Subtitle three</tt:span></tt:p>
      <tt:p xml:id="sub4" begin="00:00:06.93" end="00:00:09.92" region="bottom" style="textCenter"><tt:span style="textWhiteOnBlack">Subtitle four line one,</tt:span><tt:br/><tt:span style="textWhiteOnBlack">subtitle four line two.</tt:span></tt:p>
      <tt:p xml:id="sub5" begin="00:00:09.95" end="00:00:14.38" region="bottom" style="textCenter"><tt:span style="textWhiteOnBlack">Subtitle five line one,</tt:span><tt:br/><tt:span style="textWhiteOnBlack">subtitle five line one</tt:span></tt:p>
      <tt:p xml:id="sub6" begin="00:00:14.40" end="00:00:18.05" region="bottom" style="textCenter"><tt:span style="textWhiteOnBlack">Subtitle six line one</tt:span><tt:br/><tt:span style="textWhiteOnBlack">subtitle six line two.</tt:span></tt:p>
    </tt:div>
  </tt:body>
</tt:tt>
"""
        bad_input_etree = ElementTree.fromstring(bad_input_xml)
        vr = ValidationLogger()
        context = {}
        valid = xsd_validator.run(
            input=bad_input_etree,
            context=context,
            validation_results=vr)
        self.assertFalse(valid)
        expected_location = \
            '{http://www.w3.org/ns/ttml}span'
        expected_error_msg = \
            "Fails EBU-TT-D XSD validation: " \
            "'{http://www.w3.org/ns/ttml#styling}color' attribute " \
            "not allowed for element"
        self.assertListEqual(vr,
                             [ValidationResult(
                                 status=ERROR,
                                 location=expected_location,
                                 message=expected_error_msg,
                                 code=ValidationCode.xml_xsd)])

    def test_xsdValidator_good_input_dapt(self):
        xsd_validator = xsdValidator(
            xml_schema=DAPTSchema,
            schema_name='DAPT')
        good_input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:tta="http://www.w3.org/ns/ttml#audio"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    xmlns:ebuttm="urn:ebu:tt:metadata"
    ttp:contentProfiles="http://www.w3.org/ns/ttml/profile/dapt1.0/content"
    daptm:scriptRepresents="audio"
    daptm:scriptType="originalTranscript"
    xml:lang="en">
    <head>
        <metadata xmlns:otherns="urn:some:other:namespace">
            <ttm:agent type="person" xml:id="actor_A">
                <ttm:name type="full">Matthias Schoenaerts</ttm:name>
            </ttm:agent>
            <ttm:agent type="character" xml:id="character_2">
                <ttm:name type="alias">BOOKER</ttm:name>
                <ttm:actor agent="actor_A"/>
            </ttm:agent>
            <otherns:x/>
            <otherns:y/>
        </metadata>
    </head>
    <body>
        <div xml:id="se1" begin="3s" end="10s" ttm:agent="character_2" daptm:represents="audio.dialogue" daptm:onScreen="ON">
            <ttm:desc daptm:descType="scene">high mountain valley</ttm:desc>
            <metadata></metadata>
            <p daptm:langSrc="en"><span>Look at this beautiful valley.</span></p>
        </div>
    </body>
</tt>
"""
        good_input_etree = ElementTree.fromstring(good_input_xml)
        vr = ValidationLogger()
        context = {}
        valid = xsd_validator.run(
            input=good_input_etree,
            context=context,
            validation_results=vr)
        self.assertListEqual(vr, [
            ValidationResult(
                status=GOOD,
                location='Parsed document',
                message='DAPT XSD Validation passes',
                code=ValidationCode.xml_xsd
            )
        ])
        self.assertTrue(valid)

    def test_xsdValidator_bad_input_dapt(self):
        xsd_validator = xsdValidator(
            xml_schema=DAPTSchema,
            schema_name='DAPT'
        )
        bad_input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:tta="http://www.w3.org/ns/ttml#audio"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    xmlns:ebuttm="urn:ebu:tt:metadata"
    ttp:contentProfiles="http://www.w3.org/ns/ttml/profile/dapt1.0/content"
    daptm:scriptType="originalTranscript"
    xml:lang="en">
    <head>
        <metadata xmlns:otherns="urn:some:other:namespace">
            <ttm:agent type="person" xml:id="actor_A">
                <ttm:name type="full">Matthias Schoenaerts</ttm:name>
            </ttm:agent>
            <ttm:agent type="character" xml:id="character_2">
                <ttm:name type="alias">BOOKER</ttm:name>
                <ttm:actor agent="actor_A"/>
            </ttm:agent>
            <otherns:x/>
            <otherns:y/>
        </metadata>
    </head>
    <body>
        <div xml:id="se1" begin="3s" end="10s" ttm:agent="character_2" daptm:represents="audio.dialogue" daptm:onScreen="ON">
            <ttm:desc daptm:descType="scene">high mountain valley</ttm:desc>
            <metadata></metadata>
            <p daptm:langSrc="en"><span>Look at this beautiful valley.</span></p>
        </div>
    </body>
</tt>
"""
        bad_input_etree = ElementTree.fromstring(bad_input_xml)
        vr = ValidationLogger()
        context = {}
        valid = xsd_validator.run(
            input=bad_input_etree,
            context=context,
            validation_results=vr)
        self.assertFalse(valid)
        expected_location = \
            '{http://www.w3.org/ns/ttml}tt'
        expected_error_msg = \
            "Fails DAPT XSD validation: missing required " \
            "attribute " \
            "'{http://www.w3.org/ns/ttml/profile/dapt#metadata}scriptRepresents'"
        self.assertListEqual(vr,
                             [ValidationResult(
                                 status=ERROR,
                                 location=expected_location,
                                 message=expected_error_msg,
                                 code=ValidationCode.xml_xsd)])
