import unittest
from src.xmlChecks.xmlIdCheck import unqualifiedIdAttributeCheck, \
    duplicateXmlIdCheck, IDREFSelementApplicabilityCheck
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

    def test_IDREFS_good(self):
        """
        Test all the happy paths
        """
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
<head>
    <metadata>
        <ttm:agent xml:id="ag0" type="person"/>
        <ttm:agent xml:id="ag1" type="character">
            <actor agent="ag0"/>
        </ttm:agent>
        <ttm:agent xml:id="ag3" type="person"/>
    </metadata>
    <styling>
        <style xml:id="st0"/>
        <style xml:id="st1" style="st0"/>
    </styling>
    <layout>
        <region xml:id="r0" style="st0"/>
    </layout>
    <animation>
        <set xml:id="set0"/>
        <animate xml:id="an0"/>
    </animation>
</head>
<body>
    <div xml:id="d1" style="st1" ttm:agent="ag0 ag3" region="r0">
    <p xml:id="p1" animate="set0 an0"><span xml:id="s1">s1</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        duplicate_xml_id_check = duplicateXmlIdCheck()
        idrefs_element_applicability_check = IDREFSelementApplicabilityCheck()
        vr = ValidationLogger()
        context = {}
        valid = duplicate_xml_id_check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr.clear()
        valid &= idrefs_element_applicability_check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_IDREFS_good_wrong_ns(self):
        """
        Test all the happy paths but with the wrong root namespace
        """
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/wrong"
    xmlns:tts="http://www.w3.org/ns/wrong#styling"
    xmlns:ttp="http://www.w3.org/ns/wrong#parameter"
    xmlns:tt="http://www.w3.org/ns/wrong"
    xmlns:ttm="http://www.w3.org/ns/wrong#metadata"
    xmlns:ebuttm="urn:ebu:tt:metadata"
    xmlns:ebutts="urn:ebu:tt:style"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <metadata>
        <ttm:agent xml:id="ag0" type="person"/>
        <ttm:agent xml:id="ag1" type="character">
            <actor agent="ag0"/>
        </ttm:agent>
        <ttm:agent xml:id="ag3" type="person"/>
    </metadata>
    <styling>
        <style xml:id="st0"/>
        <style xml:id="st1" style="st0"/>
    </styling>
    <layout>
        <region xml:id="r0" style="st0"/>
    </layout>
    <animation>
        <set xml:id="set0"/>
        <animate xml:id="an0"/>
    </animation>
</head>
<body>
    <div xml:id="d1" style="st1" ttm:agent="ag0 ag3" region="r0">
    <p xml:id="p1" animate="set0 an0"><span xml:id="s1">s1</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        duplicate_xml_id_check = duplicateXmlIdCheck()
        idrefs_element_applicability_check = IDREFSelementApplicabilityCheck()
        vr = ValidationLogger()
        context = {
            'root_ns': 'http://www.w3.org/ns/wrong'
        }
        valid = duplicate_xml_id_check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr.clear()
        valid &= idrefs_element_applicability_check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
        ]
        self.assertListEqual(vr, expected_validation_results)

    # Test for IDREF with wrong number of refs
    def test_IDREF_wrong_number(self):
        """
        Test that IDREF with other than 1 value are caught
        """
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
<head>
    <metadata>
        <ttm:agent xml:id="ag0" type="person"/>
        <ttm:agent xml:id="ag1" type="character">
            <actor agent=""/></ttm:agent>
        <ttm:agent xml:id="ag3" type="person"/>
        <ttm:agent xml:id="ag4" type="character">
            <actor agent="ag0 ag3"/>
        </ttm:agent>
    </metadata>
    <styling>
        <style xml:id="st0"/>
        <style xml:id="st1" style="st0"/>
    </styling>
    <layout>
        <region xml:id="r0" style="st0"/>
    </layout>
    <animation>
        <set xml:id="set0"/>
        <animate xml:id="an0"/>
    </animation>
</head>
<body>
    <div xml:id="d1" style="st1" ttm:agent="ag0 ag3" region="r0">
    <p xml:id="p1" animate="set0 an0"><span xml:id="s1">s1</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        duplicate_xml_id_check = duplicateXmlIdCheck()
        idrefs_element_applicability_check = IDREFSelementApplicabilityCheck()
        vr = ValidationLogger()
        context = {}
        valid = duplicate_xml_id_check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr.clear()
        valid &= idrefs_element_applicability_check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}actor element agent '
                         'attribute',
                message='Attribute must reference an element',
                code=ValidationCode.ttml_idref_empty
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}actor element agent '
                         'attribute',
                message='Attribute has 2 references, 1 permitted',
                code=ValidationCode.ttml_idref_too_many
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    # Test for IDREFS pointing to not acceptable elements
    def test_IDREF_wrong_elements(self):
        """
        Test all the unhappy paths, where attributes reference
        the wrong kinds of elements
        """
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
<head>
    <metadata>
        <ttm:agent xml:id="ag0" type="person"/>
        <ttm:agent xml:id="ag1" type="character">
            <actor agent="ag0"/></ttm:agent>
        <ttm:agent xml:id="ag3" type="person"/>
        <ttm:agent xml:id="ag4" type="character">
            <actor agent="ag0 ag3"/></ttm:agent>
    </metadata>
    <styling>
        <style xml:id="st0"/>
        <style xml:id="st1" style="ag0"/>
    </styling>
    <layout>
        <region xml:id="r0" style="notaref"/>
    </layout>
    <animation>
        <set xml:id="set0"/>
        <animate xml:id="an0"/>
    </animation>
</head>
<body>
    <div xml:id="d1" style="r0" ttm:agent="ag0 st1" region="set0">
    <p xml:id="p1" animate="set0 st0"><span xml:id="s1">s1</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        duplicate_xml_id_check = duplicateXmlIdCheck()
        idrefs_element_applicability_check = IDREFSelementApplicabilityCheck()
        vr = ValidationLogger()
        context = {}
        valid = duplicate_xml_id_check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr.clear()
        valid &= idrefs_element_applicability_check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}actor element agent '
                         'attribute',
                message='Attribute has 2 references, 1 permitted',
                code=ValidationCode.ttml_idref_too_many
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}style element style '
                         'attribute reference ag0',
                message='Attribute references '
                        '{http://www.w3.org/ns/ttml#metadata}agent element, '
                        'not in the list of acceptable elements',
                code=ValidationCode.ttml_idref_element_applicability),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}region element style '
                         'attribute reference notaref',
                message='Attribute references no element, not in the list of '
                        'acceptable elements',
                code=ValidationCode.ttml_idref_element_applicability),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div element '
                         '{http://www.w3.org/ns/ttml#metadata}agent '
                         'attribute reference st1',
                message='Attribute references '
                        '{http://www.w3.org/ns/ttml}style element, not in '
                        'the list of acceptable elements',
                code=ValidationCode.ttml_idref_element_applicability),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div element region '
                         'attribute reference set0',
                message='Attribute references {http://www.w3.org/ns/ttml}set '
                        'element, not in the list of acceptable elements',
                code=ValidationCode.ttml_idref_element_applicability),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div element style '
                         'attribute reference r0',
                message='Attribute references '
                        '{http://www.w3.org/ns/ttml}region element, not in '
                        'the list of acceptable elements',
                code=ValidationCode.ttml_idref_element_applicability),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}p element animate '
                         'attribute reference st0',
                message='Attribute references '
                        '{http://www.w3.org/ns/ttml}style element, not in '
                        'the list of acceptable elements',
                code=ValidationCode.ttml_idref_element_applicability),
        ]
        self.assertListEqual(vr, expected_validation_results)
