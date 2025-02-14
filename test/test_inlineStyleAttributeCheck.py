import unittest
import src.xmlChecks.inlineStyleAttributeCheck as inlineStyleAttributeCheck
import xml.etree.ElementTree as ElementTree
from src.validationLogging.validationResult import ValidationResult, ERROR, GOOD, WARN, INFO


class testInlineStyleAttributesCheck(unittest.TestCase):
    maxDiff = None

    def test_inline_style_attributes_absent_ok(self):
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
<body style="s1"/>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        inline_style_attributes_check = \
            inlineStyleAttributeCheck.inlineStyleAttributesCheck()
        vr = []
        context = {}
        valid = inline_style_attributes_check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='content elements',
                message='Inline style attributes checked'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_inline_style_attributes_present_bad(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:itts="http://www.w3.org/ns/ttml/profile/imsc1#styling"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="s1" tts:color="#ffffffff"/>
    </styling>
</head>
<body style="s1" tts:color="white">
    <div tts:backgroundColor="red">
    <p tts:lineHeight="normal" itts:fillLineGap="true" xml:id="p1">
        <span tts:fontSize="200%">text</span>
    </p>
    </div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        inline_style_attributes_check = \
            inlineStyleAttributeCheck.inlineStyleAttributesCheck()
        vr = []
        context = {}
        valid = inline_style_attributes_check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}body xml:id=[absent]',
                message='Inline style attribute '
                        '{http://www.w3.org/ns/ttml#styling}color '
                        'not permitted on content element'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div xml:id=[absent]',
                message='Inline style attribute '
                        '{http://www.w3.org/ns/ttml#styling}backgroundColor '
                        'not permitted on content element'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}p xml:id=p1',
                message='Inline style attribute '
                        '{http://www.w3.org/ns/ttml#styling}lineHeight '
                        'not permitted on content element'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}p xml:id=p1',
                message='Inline style attribute '
                        '{http://www.w3.org/ns/ttml/profile/imsc1#styling}'
                        'fillLineGap '
                        'not permitted on content element'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}span xml:id=[absent]',
                message='Inline style attribute '
                        '{http://www.w3.org/ns/ttml#styling}fontSize '
                        'not permitted on content element'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)
