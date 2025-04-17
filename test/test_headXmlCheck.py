import unittest
import src.xmlChecks.headXmlCheck as headXmlCheck
import xml.etree.ElementTree as ElementTree
from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationResult import ValidationResult, \
    ERROR, GOOD, WARN, SKIP


class testHeadXmlCheck(unittest.TestCase):
    maxDiff = None

    ##################################
    #  Head tests                    #
    ##################################

    def test_headCheck_ok(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="s1" tts:color="#ffffffff"/>
    </styling>
    <layout>
        <region xml:id="r1" tts:origin="10% 10%"/>
    </layout>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {}
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml#metadata}copyright',
                message='Copyright element found',
                code=ValidationCode.ttml_metadata_copyright
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found',
                code=ValidationCode.ebuttd_styling_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}styling/'
                         '{http://www.w3.org/ns/ttml}style]',
                message='Style elements checked',
                code=ValidationCode.ttml_element_styling
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}layout',
                message='layout element found',
                code=ValidationCode.ebuttd_layout_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}layout/'
                         '{http://www.w3.org/ns/ttml}region]',
                message='Region elements checked',
                code=ValidationCode.ttml_element_layout
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt/'
                         '{http://www.w3.org/ns/ttml}head',
                message='Head checked',
                code=ValidationCode.ttml_element_head
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_headCheck_ok_wrong_ns(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttaf"
    xmlns:tts="http://www.w3.org/ns/ttaf#styling"
    xmlns:ttp="http://www.w3.org/ns/ttaf#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttaf#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid</ttm:copyright>
    <styling>
        <style xml:id="s1" tts:color="#ffffffff"/>
    </styling>
    <layout>
        <region xml:id="r1" tts:origin="10% 10%"/>
    </layout>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {
            'root_ns': 'http://www.w3.org/ns/ttaf'
        }
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttaf}head/'
                         '{http://www.w3.org/ns/ttaf#metadata}copyright',
                message='Copyright element found',
                code=ValidationCode.ttml_metadata_copyright
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttaf}head/'
                         '{http://www.w3.org/ns/ttaf}styling',
                message='styling element found',
                code=ValidationCode.ebuttd_styling_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttaf}styling/'
                         '{http://www.w3.org/ns/ttaf}style]',
                message='Style elements checked',
                code=ValidationCode.ttml_element_styling
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttaf}head/'
                         '{http://www.w3.org/ns/ttaf}layout',
                message='layout element found',
                code=ValidationCode.ebuttd_layout_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttaf}layout/'
                         '{http://www.w3.org/ns/ttaf}region]',
                message='Region elements checked',
                code=ValidationCode.ttml_element_layout
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttaf}tt/'
                         '{http://www.w3.org/ns/ttaf}head',
                message='Head checked',
                code=ValidationCode.ttml_element_head
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_headCheck_head_missing(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {}
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_result = ValidationResult(
            status=ERROR,
            location='{http://www.w3.org/ns/ttml}tt/'
                     '{http://www.w3.org/ns/ttml}head',
            message='Found 0 head elements, expected 1',
            code=ValidationCode.ebuttd_head_element_constraint
        )
        self.assertListEqual(vr, [expected_validation_result])

    def test_headCheck_head_too_many(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml">
<head></head>
<head></head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {}
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_result = ValidationResult(
            status=ERROR,
            location='{http://www.w3.org/ns/ttml}tt/'
                     '{http://www.w3.org/ns/ttml}head',
            message='Found 2 head elements, expected 1',
            code=ValidationCode.ttml_element_head
        )
        self.assertListEqual(vr, [expected_validation_result])

    ##################################
    #  Copyright tests               #
    ##################################

    def test_headCheck_copyright_missing_optional(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
<head>
    <styling>
        <style xml:id="s1" tts:color="#ffffffff"/>
    </styling>
    <layout>
        <region xml:id="r1" tts:origin="10% 10%"/>
    </layout>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {}
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=WARN,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml#metadata}copyright',
                message='copyright element absent',
                code=ValidationCode.ttml_metadata_copyright
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found',
                code=ValidationCode.ebuttd_styling_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}styling/'
                         '{http://www.w3.org/ns/ttml}style]',
                message='Style elements checked',
                code=ValidationCode.ttml_element_styling
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}layout',
                message='layout element found',
                code=ValidationCode.ebuttd_layout_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}layout/'
                         '{http://www.w3.org/ns/ttml}region]',
                message='Region elements checked',
                code=ValidationCode.ttml_element_layout
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt/'
                         '{http://www.w3.org/ns/ttml}head',
                message='Head checked',
                code=ValidationCode.ttml_element_head
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_headCheck_copyright_missing_required(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
<head>
    <styling>
        <style xml:id="s1" tts:color="#ffffffff"/>
    </styling>
    <layout>
        <region xml:id="r1" tts:origin="10% 10%"/>
    </layout>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=True
        )
        vr = ValidationLogger()
        context = {}
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml#metadata}copyright',
                message='Required copyright element absent',
                code=ValidationCode.ttml_metadata_copyright
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found',
                code=ValidationCode.ebuttd_styling_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}styling/'
                         '{http://www.w3.org/ns/ttml}style]',
                message='Style elements checked',
                code=ValidationCode.ttml_element_styling
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}layout',
                message='layout element found',
                code=ValidationCode.ebuttd_layout_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}layout/'
                         '{http://www.w3.org/ns/ttml}region]',
                message='Region elements checked',
                code=ValidationCode.ttml_element_layout
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_headCheck_copyright_too_many_wrong_ns(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttaf"
    xmlns:ttp="http://www.w3.org/ns/ttaf#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttaf#metadata"
    xmlns:tts="http://www.w3.org/ns/ttaf#styling"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid</ttm:copyright>
    <ttm:copyright>strange</ttm:copyright>
    <styling>
        <style xml:id="s1" tts:color="#ffffffff"/>
    </styling>
    <layout>
        <region xml:id="r1" tts:origin="10% 10%"/>
    </layout>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {
            'root_ns': 'http://www.w3.org/ns/ttaf'
        }
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=WARN,
                location='{http://www.w3.org/ns/ttaf}head/'
                         '{http://www.w3.org/ns/ttaf#metadata}copyright',
                message='2 copyright elements found, expected 1',
                code=ValidationCode.ttml_metadata_copyright
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttaf}head/'
                         '{http://www.w3.org/ns/ttaf}styling',
                message='styling element found',
                code=ValidationCode.ebuttd_styling_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttaf}styling/'
                         '{http://www.w3.org/ns/ttaf}style]',
                message='Style elements checked',
                code=ValidationCode.ttml_element_styling
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttaf}head/'
                         '{http://www.w3.org/ns/ttaf}layout',
                message='layout element found',
                code=ValidationCode.ebuttd_layout_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttaf}layout/'
                         '{http://www.w3.org/ns/ttaf}region]',
                message='Region elements checked',
                code=ValidationCode.ttml_element_layout
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttaf}tt/'
                         '{http://www.w3.org/ns/ttaf}head',
                message='Head checked',
                code=ValidationCode.ttml_element_head
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    ##################################
    #  Styling and style tests       #
    ##################################

    def test_headCheck_styling_missing(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <layout>
        <region xml:id="r1" tts:origin="10% 10%"/>
    </layout>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {}
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml#metadata}copyright',
                message='Copyright element found',
                code=ValidationCode.ttml_metadata_copyright
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='Required styling element absent',
                code=ValidationCode.ebuttd_styling_element_constraint
            ),
            ValidationResult(
                status=SKIP,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='Skipping style element checks',
                code=ValidationCode.ttml_element_style
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}layout',
                message='layout element found',
                code=ValidationCode.ebuttd_layout_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}layout/'
                         '{http://www.w3.org/ns/ttml}region]',
                message='Region elements checked',
                code=ValidationCode.ttml_element_layout
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_headCheck_too_many_styling(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling/>
    <styling/>
    <layout>
        <region xml:id="r1" tts:origin="10% 10%"/>
    </layout>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {}
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml#metadata}copyright',
                message='Copyright element found',
                code=ValidationCode.ttml_metadata_copyright
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='2 styling elements found, expected 1',
                code=ValidationCode.ttml_element_styling
            ),
            ValidationResult(
                status=SKIP,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='Skipping style element checks',
                code=ValidationCode.ttml_element_style
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}layout',
                message='layout element found',
                code=ValidationCode.ebuttd_layout_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}layout/'
                         '{http://www.w3.org/ns/ttml}region]',
                message='Region elements checked',
                code=ValidationCode.ttml_element_layout
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_headCheck_styles_missing(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
    </styling>
    <layout>
        <region xml:id="r1" tts:origin="10% 10%"/>
    </layout>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {}
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml#metadata}copyright',
                message='Copyright element found',
                code=ValidationCode.ttml_metadata_copyright
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found',
                code=ValidationCode.ebuttd_styling_element_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}styling/'
                         '{http://www.w3.org/ns/ttml}style',
                message='At least one style element required, none found',
                code=ValidationCode.ebuttd_style_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}layout',
                message='layout element found',
                code=ValidationCode.ebuttd_layout_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}layout/'
                         '{http://www.w3.org/ns/ttml}region]',
                message='Region elements checked',
                code=ValidationCode.ttml_element_layout
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_headCheck_style_no_xml_id(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style tts:color="#ffffffff"/>
    </styling>
    <layout>
        <region xml:id="r1" tts:origin="10% 10%"/>
    </layout>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {}
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml#metadata}copyright',
                message='Copyright element found',
                code=ValidationCode.ttml_metadata_copyright
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found',
                code=ValidationCode.ebuttd_styling_element_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}style@'
                         '{http://www.w3.org/XML/1998/namespace}id',
                message='style element found with no xml:id',
                code=ValidationCode.ttml_element_style
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}layout',
                message='layout element found',
                code=ValidationCode.ebuttd_layout_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}layout/'
                         '{http://www.w3.org/ns/ttml}region]',
                message='Region elements checked',
                code=ValidationCode.ttml_element_layout
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_headCheck_style_no_style_attribs(self):
        pass
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="s1"/>
        <style unknown="blah"/>
    </styling>
    <layout>
        <region xml:id="r1" tts:origin="10% 10%"/>
    </layout>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {}
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml#metadata}copyright',
                message='Copyright element found',
                code=ValidationCode.ttml_metadata_copyright
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found',
                code=ValidationCode.ebuttd_styling_element_constraint
            ),
            ValidationResult(
                status=WARN,
                location='{http://www.w3.org/ns/ttml}style '
                         's1',
                message='Style element has no recognised style attributes',
                code=ValidationCode.ttml_element_style
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}style@'
                         '{http://www.w3.org/XML/1998/namespace}id',
                message='style element found with no xml:id',
                code=ValidationCode.ttml_element_style
            ),
            ValidationResult(
                status=WARN,
                location='{http://www.w3.org/ns/ttml}style '
                         '(no xml:id)',
                message='Style element has no recognised style attributes',
                code=ValidationCode.ttml_element_style
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}layout',
                message='layout element found',
                code=ValidationCode.ebuttd_layout_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}layout/'
                         '{http://www.w3.org/ns/ttml}region]',
                message='Region elements checked',
                code=ValidationCode.ttml_element_layout
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_headCheck_style_invalid_attribs(self):
        pass
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ebutts="urn:ebu:tt:style"
    xmlns:itts="http://www.w3.org/ns/ttml/profile/imsc1#styling"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="s1"
            tts:color="white"
            ebutts:linePadding="1%"
            itts:fillLineGap="curious"/>
    </styling>
    <layout>
        <region xml:id="r1" tts:origin="10% 10%"/>
    </layout>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {}
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml#metadata}copyright',
                message='Copyright element found',
                code=ValidationCode.ttml_metadata_copyright
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found',
                code=ValidationCode.ebuttd_styling_element_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}style@'
                         '{http://www.w3.org/ns/ttml#styling}color',
                message='Attribute value [white] is invalid',
                code=ValidationCode.ttml_attribute_styling_attribute
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}style@'
                         '{urn:ebu:tt:style}linePadding',
                message='Attribute value [1%] is invalid',
                code=ValidationCode.ttml_attribute_styling_attribute
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}style@'
                         '{http://www.w3.org/ns/ttml/profile/imsc1#styling}'
                         'fillLineGap',
                message='Attribute value [curious] is invalid',
                code=ValidationCode.ttml_attribute_styling_attribute
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}layout',
                message='layout element found',
                code=ValidationCode.ebuttd_layout_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}layout/'
                         '{http://www.w3.org/ns/ttml}region]',
                message='Region elements checked',
                code=ValidationCode.ttml_element_layout
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    ##################################
    #  Layout and region tests       #
    ##################################

    def test_headCheck_layout_missing(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="s1" tts:fontSize="100%"/>
    </styling>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {}
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml#metadata}copyright',
                message='Copyright element found',
                code=ValidationCode.ttml_metadata_copyright
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found',
                code=ValidationCode.ebuttd_styling_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}styling/'
                         '{http://www.w3.org/ns/ttml}style]',
                message='Style elements checked',
                code=ValidationCode.ttml_element_styling
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}layout',
                message='Required layout element absent',
                code=ValidationCode.ebuttd_layout_element_constraint
            ),
            ValidationResult(
                status=SKIP,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}layout',
                message='Skipping region element checks',
                code=ValidationCode.ttml_element_region
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_headCheck_too_many_layout(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="s1" tts:fontSize="100%"/>
    </styling>
    <layout/>
    <layout/>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {}
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml#metadata}copyright',
                message='Copyright element found',
                code=ValidationCode.ttml_metadata_copyright
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found',
                code=ValidationCode.ebuttd_styling_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}styling/'
                         '{http://www.w3.org/ns/ttml}style]',
                message='Style elements checked',
                code=ValidationCode.ttml_element_styling
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}layout',
                message='2 layout elements found, expected 1',
                code=ValidationCode.ttml_element_layout
            ),
            ValidationResult(
                status=SKIP,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}layout',
                message='Skipping region element checks',
                code=ValidationCode.ttml_element_region
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_headCheck_regions_missing(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="s1" tts:fontSize="100%"/>
    </styling>
    <layout>
    </layout>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {}
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml#metadata}copyright',
                message='Copyright element found',
                code=ValidationCode.ttml_metadata_copyright
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found',
                code=ValidationCode.ebuttd_styling_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}styling/'
                         '{http://www.w3.org/ns/ttml}style]',
                message='Style elements checked',
                code=ValidationCode.ttml_element_styling
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}layout',
                message='layout element found',
                code=ValidationCode.ebuttd_layout_element_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}layout/'
                         '{http://www.w3.org/ns/ttml}region',
                message='At least one region element required, none found',
                code=ValidationCode.ebuttd_region_element_constraint
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_headCheck_region_no_xml_id(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="s1" tts:color="#ffffffff"/>
    </styling>
    <layout>
        <region tts:origin="10% 10%"/>
    </layout>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {}
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml#metadata}copyright',
                message='Copyright element found',
                code=ValidationCode.ttml_metadata_copyright
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found',
                code=ValidationCode.ebuttd_styling_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}styling/'
                         '{http://www.w3.org/ns/ttml}style]',
                message='Style elements checked',
                code=ValidationCode.ttml_element_styling
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}layout',
                message='layout element found',
                code=ValidationCode.ebuttd_layout_element_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}region@'
                         '{http://www.w3.org/XML/1998/namespace}id',
                message='region element found with no xml:id',
                code=ValidationCode.ttml_element_region
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_headCheck_region_no_style_attribs(self):
        pass
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="s1" tts:fontSize="100%"/>
    </styling>
    <layout>
        <region xml:id="r1"/>
        <region unknown="blah"/>
    </layout>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {}
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml#metadata}copyright',
                message='Copyright element found',
                code=ValidationCode.ttml_metadata_copyright
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found',
                code=ValidationCode.ebuttd_styling_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}styling/'
                         '{http://www.w3.org/ns/ttml}style]',
                message='Style elements checked',
                code=ValidationCode.ttml_element_styling
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}layout',
                message='layout element found',
                code=ValidationCode.ebuttd_layout_element_constraint
            ),
            ValidationResult(
                status=WARN,
                location='{http://www.w3.org/ns/ttml}region '
                         'r1',
                message='Region element has no recognised style attributes',
                code=ValidationCode.ttml_element_region
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}region@'
                         '{http://www.w3.org/XML/1998/namespace}id',
                message='region element found with no xml:id',
                code=ValidationCode.ttml_element_region
            ),
            ValidationResult(
                status=WARN,
                location='{http://www.w3.org/ns/ttml}region '
                         '(no xml:id)',
                message='Region element has no recognised style attributes',
                code=ValidationCode.ttml_element_region
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_headCheck_region_invalid_attribs(self):
        pass
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ebutts="urn:ebu:tt:style"
    xmlns:itts="http://www.w3.org/ns/ttml/profile/imsc1#styling"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="s1" tts:color="#ffffff"/>
    </styling>
    <layout>
        <region xml:id="r1"
            tts:origin="the big bang"
            tts:extent="mahoosive"
            tts:backgroundColor="purple"/>
    </layout>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = ValidationLogger()
        context = {}
        valid = headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml#metadata}copyright',
                message='Copyright element found',
                code=ValidationCode.ttml_metadata_copyright
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found',
                code=ValidationCode.ebuttd_styling_element_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}styling/'
                         '{http://www.w3.org/ns/ttml}style]',
                message='Style elements checked',
                code=ValidationCode.ttml_element_styling
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}layout',
                message='layout element found',
                code=ValidationCode.ebuttd_layout_element_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}region@'
                         '{http://www.w3.org/ns/ttml#styling}origin',
                message='Attribute value [the big bang] is invalid',
                code=ValidationCode.ttml_attribute_styling_attribute
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}region@'
                         '{http://www.w3.org/ns/ttml#styling}extent',
                message='Attribute value [mahoosive] is invalid',
                code=ValidationCode.ttml_attribute_styling_attribute
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}region@'
                         '{http://www.w3.org/ns/ttml#styling}'
                         'backgroundColor',
                message='Attribute value [purple] is invalid',
                code=ValidationCode.ttml_attribute_styling_attribute
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)
