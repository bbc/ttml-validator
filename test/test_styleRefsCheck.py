import unittest
import src.xmlChecks.styleRefsCheck as styleRefsCheck
import src.xmlChecks.headXmlCheck as headXmlCheck
import src.xmlChecks.ttXmlCheck as ttXmlCheck
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
        <style xml:id="style_bbc_ok"
            tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
            tts:lineHeight="120%"/>
    </styling>
</head>
<body style="not_an_id">
<div xml:id="d1"><p style="style_bbc_ok d1"></p></div>
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
                status=INFO,
                location='p element xml:id omitted',
                message='Computed fontSize 6.666667rh (within BBC-allowed range)'
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
        <style xml:id="style_bbc_ok"
            tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
            tts:lineHeight="120%"/>
    </styling>
</head>
<body>
<div><p xml:id="d1" style="style_bbc_ok"><span style="s1">text</span></p></div>
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
        expected_validation_error_results = [
            ValidationResult(
                status=ERROR,
                location='span element',
                message='Specified style attribute '
                        '{http://www.w3.org/ns/ttml#styling}lineHeight '
                        'is not applicable to element type span'
            ),
        ]
        vr_errors = [r for r in vr if r.status == ERROR]
        self.assertListEqual(
            vr_errors,
            expected_validation_error_results)

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
        <style xml:id="style_bbc_ok"
            tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
            tts:lineHeight="120%"/>
        <style xml:id="s1" tts:color="#ffffff" style="s2"/>
        <style xml:id="s2" tts:fontSize="120%" style="s1"/>
        <style xml:id="s3" style="s4"/>
        <style xml:id="s4" style="s5"/>
        <style xml:id="s5" style="s3"/>
    </styling>
</head>
<body>
<div style="style_bbc_ok"><p xml:id="d1"><span style="s1">text</span></p></div>
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
        expected_validation_error_results = [
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
        vr_errors = [r for r in vr if r.status == ERROR]
        self.assertListEqual(
            vr_errors,
            expected_validation_error_results)

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
        <style xml:id="style_bbc_ok"
            tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
            tts:lineHeight="120%"/>
        <style xml:id="s1" tts:backgroundColor="#000000"/>
        <style xml:id="s2" tts:backgroundColor="#00000000"/>
        <style xml:id="s3" tts:backgroundColor="[bogus value]"/>
    </styling>
</head>
<body style="s1 s3 style_bbc_ok">
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
        expected_validation_error_results = [
            ValidationResult(
                status=ERROR,
                location='body element {http://www.w3.org/ns/ttml#styling}backgroundColor attribute',
                message='backgroundColor attribute '
                        '[bogus value] '
                        'is not valid'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml#styling}backgroundColor '
                         'styling attribute with value "[bogus value]"',
                message='Value has invalid format'
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
        vr_errors = [r for r in vr if r.status == ERROR]
        self.assertListEqual(
            vr_errors,
            expected_validation_error_results)

    def test_fontFamily_ok(self):
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
        <style xml:id="s1" tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"/>
    </styling>
</head>
<body style="s1">
<div><p xml:id="d1" style="s1"><span>text</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = []
        context = {}
        # cellResolutionCheck is a dependency so it populates
        # context['cellResolution']
        cellResolutionCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
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

    def test_fontFamily_bad(self):
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
        <style xml:id="s1" tts:fontFamily="jelly, ice cream, default"/>
    </styling>
</head>
<body style="s1">
<div><p xml:id="d1" style="s1"><span>text</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = []
        context = {}
        # cellResolutionCheck is a dependency so it populates
        # context['cellResolution']
        cellResolutionCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
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
        expected_validation_error_results = [
            ValidationResult(
                status=ERROR,
                location='p element xml:id d1',
                message="Computed fontFamily "
                        "['jelly', 'ice cream', 'default'] "
                        "differs from BBC requirement"
            ),
            ValidationResult(
                status=ERROR,
                location='span element xml:id omitted',
                message="Computed fontFamily "
                        "['jelly', 'ice cream', 'default'] "
                        "differs from BBC requirement"
            ),
        ]
        vr_errors = [r for r in vr if r.status == ERROR]
        self.assertListEqual(
            vr_errors,
            expected_validation_error_results)

    def test_fontSize_ok(self):
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
        <style xml:id="s1"
        tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
        tts:fontSize="75%"/>
    </styling>
</head>
<body>
<div><p xml:id="d1" style="s1"><span style="s1">text</span><span tts:fontSize="150%">big</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = []
        context = {}
        # cellResolutionCheck is a dependency so it populates
        # context['cellResolution']
        cellResolutionCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
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

    def test_fontSize_bad(self):
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
        <style xml:id="fontStyle"
        tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"/>
        <style xml:id="fontSize1"
        tts:fontSize="75%"/>
        <style xml:id="fontSize2"
        tts:fontSize="200%"/>
    </styling>
</head>
<body style="fontStyle">
<div><p xml:id="d1" style="fontSize1"><span style="fontSize1">text</span><span tts:fontSize="20%">tiny</span></p></div>
<div><p xml:id="d2" style="fontSize2"><span style="fontSize2" xml:id="sp3">text</span><span xml:id="sp4" tts:fontSize="20%">tiny</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = []
        context = {}
        # cellResolutionCheck is a dependency so it populates
        # context['cellResolution']
        cellResolutionCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
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
        expected_validation_error_results = [
            ValidationResult(
                status=ERROR,
                location='span element xml:id omitted',
                message="Computed fontSize "
                        "1.000000rh "
                        "outside BBC-allowed range"
            ),
            ValidationResult(
                status=ERROR,
                location='p element xml:id d2',
                message="Computed fontSize "
                        "13.333334rh "
                        "outside BBC-allowed range"
            ),
            ValidationResult(
                status=ERROR,
                location='span element xml:id sp3',
                message="Computed fontSize "
                        "26.666668rh "
                        "outside BBC-allowed range"
            ),
        ]
        vr_errors = [r for r in vr if r.status == ERROR]
        self.assertListEqual(
            vr_errors,
            expected_validation_error_results)
