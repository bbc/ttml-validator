import unittest
from src.xmlChecks.xmlIdCheck import unqualifiedIdAttributeCheck, \
    duplicateXmlIdCheck
import xml.etree.ElementTree as ElementTree
from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationResult import ValidationResult, \
    ERROR, GOOD, WARN


class testXmlIdCheck(unittest.TestCase):
    maxDiff = None

    def test_unqualifiedIdAttributeCheck(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml">
<head>
<styling>
<style xml:id="s1"/>
<style xml:id="s2" id="s2"/>
<style id="s3"/></styling>
</head>
</tt>"""
        input_elementtree = ElementTree.fromstring(input_xml)
        unqualified_id_attribute_check = unqualifiedIdAttributeCheck()
        vr = ValidationLogger()
        context = {}
        valid = unqualified_id_attribute_check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=WARN,
                location='Parsed document',
                message='2 elements have unqualified id attributes, '
                        'of which 1 have no xml:id attribute. '
                        'Check if they should have xml:id attributes!',
                code=ValidationCode.xml_id_unqualified
            ),
            ]
        self.assertListEqual(vr, expected_validation_results)

    def test_xmlIdCheck_no_duplicates(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:tt="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ebuttm="urn:ebu:tt:metadata"
    xmlns:ebutts="urn:ebu:tt:style"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body>
<div xml:id="d1"><p xml:id="p1"><span xml:id="s1">s1</span></p></div>
<div xml:id="d2"><p xml:id="p2"><span xml:id="s2">s2</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        duplicate_xml_id_check = duplicateXmlIdCheck()
        vr = ValidationLogger()
        context = {}
        valid = duplicate_xml_id_check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_result = ValidationResult(
            status=GOOD,
            location='Parsed document',
            message='xml:id values are unique',
            code=ValidationCode.xml_id_unique
        )
        self.assertListEqual(vr, [expected_validation_result])

    def test_xmlIdCheck_duplicates(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:tt="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ebuttm="urn:ebu:tt:metadata"
    xmlns:ebutts="urn:ebu:tt:style"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body>
<div xml:id="d1"><p xml:id="p1"><span xml:id="s1">s1</span></p></div>
<div xml:id="d1"><p xml:id="p1"><span xml:id="s2">s2</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        duplicate_xml_id_check = duplicateXmlIdCheck()
        vr = ValidationLogger()
        context = {}
        valid = duplicate_xml_id_check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div, '
                         '{http://www.w3.org/ns/ttml}div',
                message='Duplicate xml:id found with value d1',
                code=ValidationCode.xml_id_unique
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}p, '
                         '{http://www.w3.org/ns/ttml}p',
                message='Duplicate xml:id found with value p1',
                code=ValidationCode.xml_id_unique
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)
