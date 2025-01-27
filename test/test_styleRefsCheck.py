import unittest
import src.xmlChecks.styleRefsCheck as styleRefsCheck
import src.xmlChecks.headXmlCheck as headXmlCheck
import xml.etree.ElementTree as ElementTree
from src.validationResult import ValidationResult, ERROR, GOOD, WARN, INFO


class testStyleRefsCheck(unittest.TestCase):
    maxDiff = None

    def test_style_refs_ok(self):
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
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        vr = []
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr = []
        valid = stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='document',
                message='Style references and attributes checked'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_style_refs_unref_style(self):
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
<body/>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        vr = []
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr = []
        valid = stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=WARN,
                location='style xml:id=s1',
                message='Unreferenced style element'
            ),
            ValidationResult(
                status=GOOD,
                location='document',
                message='Style references and attributes checked'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_style_refs_ref_not_style(self):
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
<body style="not_an_id">
<div xml:id="d1"><p style="d1"></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        vr = []
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr = []
        valid = stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=WARN,
                location='style xml:id=not_an_id',
                message='Referenced id does not point to a style element'
            ),
            ValidationResult(
                status=WARN,
                location='style xml:id=d1',
                message='Referenced id does not point to a style element'
            ),
            ValidationResult(
                status=GOOD,
                location='document',
                message='Style references and attributes checked'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_style_attrib_not_applicable_to_span(self):
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
        <style xml:id="s1" tts:lineHeight="150%"/>
    </styling>
</head>
<body>
<div><p xml:id="d1"><span style="s1">text</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        vr = []
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr = []
        valid = stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='span element',
                message='Specified style attribute '
                        '{http://www.w3.org/ns/ttml#styling}lineHeight '
                        'is not applicable to element type span'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_cyclic_style_refs(self):
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
        <style xml:id="s1" tts:color="#ffffff" style="s2"/>
        <style xml:id="s2" tts:fontSize="120%" style="s1"/>
        <style xml:id="s3" style="s4"/>
        <style xml:id="s4" style="s5"/>
        <style xml:id="s5" style="s3"/>
    </styling>
</head>
<body>
<div><p xml:id="d1"><span style="s1">text</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        vr = []
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr = []
        valid = stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='style element',
                message='Cyclic style ref to s2 found'
            ),
            ValidationResult(
                status=ERROR,
                location='style element',
                message='Cyclic style ref to s1 found'
            ),
            ValidationResult(
                status=ERROR,
                location='style element',
                message='Cyclic style ref to s4 found'
            ),
            ValidationResult(
                status=ERROR,
                location='style element',
                message='Cyclic style ref to s5 found'
            ),
            ValidationResult(
                status=ERROR,
                location='style element',
                message='Cyclic style ref to s3 found'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_background_color_unset_on_non_span(self):
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
        <style xml:id="s1" tts:backgroundColor="#000000"/>
        <style xml:id="s2" tts:backgroundColor="#00000000"/>
        <style xml:id="s3" tts:backgroundColor="[bogus value]"/>
    </styling>
</head>
<body style="s1 s3">
<div style="s2"><p xml:id="d1" style="s1"><span style="s1">text</span><span style="s2"> more text</span></p></div>
<div style="s2" tts:backgroundColor="#ff0000"><p xml:id="d2"><span></span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        vr = []
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr = []
        valid = stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='body element {http://www.w3.org/ns/ttml#styling}backgroundColor attribute',
                message='backgroundColor attribute '
                        '[bogus value] '
                        'is not valid'
            ),
            ValidationResult(
                status=ERROR,
                location='p element {http://www.w3.org/ns/ttml#styling}backgroundColor attribute',
                message='backgroundColor #000000 '
                        'is not transparent (BBC requirement)'
            ),
            ValidationResult(
                status=ERROR,
                location='div element {http://www.w3.org/ns/ttml#styling}backgroundColor attribute',
                message='backgroundColor #ff0000 '
                        'is not transparent (BBC requirement)'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)
