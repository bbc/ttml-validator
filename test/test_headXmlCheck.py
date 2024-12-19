import unittest
import src.xmlChecks.headXmlCheck as headXmlCheck
import xml.etree.ElementTree as ElementTree
from src.validationResult import ValidationResult, ERROR, GOOD, WARN, INFO


class testheadXmlCheck(unittest.TestCase):
    maxDiff = None

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
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = []
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
                message='Copyright element found'
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found'
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}styling/'
                         '{http://www.w3.org/ns/ttml}style]',
                message='Style elements checked'
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt/'
                         '{http://www.w3.org/ns/ttml}head',
                message='Head checked'
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
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = []
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
                message='Copyright element found'
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttaf}head/'
                         '{http://www.w3.org/ns/ttaf}styling',
                message='styling element found'
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttaf}styling/'
                         '{http://www.w3.org/ns/ttaf}style]',
                message='Style elements checked'
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttaf}tt/'
                         '{http://www.w3.org/ns/ttaf}head',
                message='Head checked'
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
        vr = []
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
            message='Found 0 head elements, expected 1'
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
        vr = []
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
            message='Found 2 head elements, expected 1'
        )
        self.assertListEqual(vr, [expected_validation_result])

    def test_headCheck_copyright_missing_optional(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
<head>
    <styling>
        <style xml:id="s1" tts:color="#ffffffff"/>
    </styling>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = []
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
                message='copyright element absent'
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found'
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}styling/'
                         '{http://www.w3.org/ns/ttml}style]',
                message='Style elements checked'
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt/'
                         '{http://www.w3.org/ns/ttml}head',
                message='Head checked'
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
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=True
        )
        vr = []
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
                message='Required copyright element absent'
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found'
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttml}styling/'
                         '{http://www.w3.org/ns/ttml}style]',
                message='Style elements checked'
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
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = []
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
                message='2 copyright elements found, expected 1'
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttaf}head/'
                         '{http://www.w3.org/ns/ttaf}styling',
                message='styling element found'
            ),
            ValidationResult(
                status=GOOD,
                location='[{http://www.w3.org/ns/ttaf}styling/'
                         '{http://www.w3.org/ns/ttaf}style]',
                message='Style elements checked'
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttaf}tt/'
                         '{http://www.w3.org/ns/ttaf}head',
                message='Head checked'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_headCheck_styling_missing(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = []
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
                message='Copyright element found'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='Required styling element absent'
            ),
            ValidationResult(
                status=WARN,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='Skipping style element checks'
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
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = []
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
                message='Copyright element found'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='2 styling elements found, expected 1'
            ),
            ValidationResult(
                status=WARN,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='Skipping style element checks'
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
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = []
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
                message='Copyright element found'
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}styling/'
                         '{http://www.w3.org/ns/ttml}style',
                message='At least one style element required, none found'
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
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = []
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
                message='Copyright element found'
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}style@'
                         '{http://www.w3.org/XML/1998/namespace}id',
                message='style element found with no xml:id'
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
</head>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        headCheck = headXmlCheck.headCheck(
            copyright_required=False
        )
        vr = []
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
                message='Copyright element found'
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}styling',
                message='styling element found'
            ),
            ValidationResult(
                status=WARN,
                location='{http://www.w3.org/ns/ttml}style '
                         's1',
                message='Style element has no recognised style attributes'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}style@'
                         '{http://www.w3.org/XML/1998/namespace}id',
                message='style element found with no xml:id'
            ),
            ValidationResult(
                status=WARN,
                location='{http://www.w3.org/ns/ttml}style '
                         '(no xml:id)',
                message='Style element has no recognised style attributes'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)
