import unittest
import src.xmlChecks.styleRefsCheck as styleRefsCheck
import src.xmlChecks.headXmlCheck as headXmlCheck
import src.xmlChecks.stylingCheck as stylingCheck
import src.xmlChecks.layoutCheck as layoutCheck
import src.xmlChecks.ttXmlCheck as ttXmlCheck
import xml.etree.ElementTree as ElementTree
from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationResult import ValidationResult, \
    ERROR, GOOD, WARN, INFO


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
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        vr = ValidationLogger()
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr = ValidationLogger()
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
                message='Style references and attributes checked',
                code=ValidationCode.ttml_styling
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
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        vr = ValidationLogger()
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr = ValidationLogger()
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
                message='Unreferenced style element',
                code=ValidationCode.ttml_element_style
            ),
            ValidationResult(
                status=GOOD,
                location='document',
                message='Style references and attributes checked',
                code=ValidationCode.ttml_styling
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
    xmlns:ebutts="urn:ebu:tt:style"
    xmlns:itts="http://www.w3.org/ns/ttml/profile/imsc1#styling"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="style_bbc_ok"
            tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
            tts:lineHeight="120%" ebutts:linePadding="0.5c" itts:fillLineGap="true"/>
    </styling>
</head>
<body style="not_an_id">
<div xml:id="d1"><p style="style_bbc_ok d1"></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        vr = ValidationLogger()
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr = ValidationLogger()
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
                message='Referenced id does not point to a style element',
                code=ValidationCode.ttml_styling_reference
            ),
            ValidationResult(
                status=WARN,
                location='style xml:id=d1',
                message='Referenced id does not point to a style element',
                code=ValidationCode.ttml_styling_reference
            ),
            ValidationResult(
                status=GOOD,
                location='p element xml:id omitted',
                message='Computed fontSize 6.667rh '
                        '(within BBC-allowed range)',
                code=ValidationCode.bbc_text_fontSize_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='p element xml:id omitted',
                message='Computed linePadding 0.5c within BBC-allowed range',
                code=ValidationCode.bbc_text_linePadding_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='document',
                message='Style references and attributes checked',
                code=ValidationCode.ttml_styling
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
    xmlns:ebutts="urn:ebu:tt:style"
    xmlns:itts="http://www.w3.org/ns/ttml/profile/imsc1#styling"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="s1" tts:lineHeight="150%" tts:backgroundColor="#000000"/>
        <style xml:id="style_bbc_ok"
            tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
            tts:lineHeight="120%" ebutts:linePadding="0.5c"
            itts:fillLineGap="true" tts:color="#ffffff"/>
    </styling>
</head>
<body>
<div><p xml:id="d1" style="style_bbc_ok"><span style="s1">text</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        vr = ValidationLogger()
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr = ValidationLogger()
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
                        'is not applicable to element type span',
                code=ValidationCode.ttml_styling_attribute_applicability
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
    xmlns:ebutts="urn:ebu:tt:style"
    xmlns:itts="http://www.w3.org/ns/ttml/profile/imsc1#styling"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="style_bbc_ok"
            tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
            tts:lineHeight="120%" ebutts:linePadding="0.5c"
            itts:fillLineGap="true"/>
        <style xml:id="s1" tts:color="#ffffff" tts:backgroundColor="#000000"
            style="s2"/>
        <style xml:id="s2" tts:fontSize="105%" style="s1"/>
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
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        vr = ValidationLogger()
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr = ValidationLogger()
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
                message='Cyclic style ref to s2 found',
                code=ValidationCode.ttml_styling_referential_chained
            ),
            ValidationResult(
                status=ERROR,
                location='style element',
                message='Cyclic style ref to s1 found',
                code=ValidationCode.ttml_styling_referential_chained
            ),
            ValidationResult(
                status=ERROR,
                location='style element',
                message='Cyclic style ref to s4 found',
                code=ValidationCode.ttml_styling_referential_chained
            ),
            ValidationResult(
                status=ERROR,
                location='style element',
                message='Cyclic style ref to s5 found',
                code=ValidationCode.ttml_styling_referential_chained
            ),
            ValidationResult(
                status=ERROR,
                location='style element',
                message='Cyclic style ref to s3 found',
                code=ValidationCode.ttml_styling_referential_chained
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
    xmlns:ebutts="urn:ebu:tt:style"
    xmlns:itts="http://www.w3.org/ns/ttml/profile/imsc1#styling"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="style_bbc_ok"
            tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
            tts:lineHeight="120%" ebutts:linePadding="0.5c" itts:fillLineGap="true"/>
        <style xml:id="s1" tts:backgroundColor="#000000"/>
        <style xml:id="s2" tts:backgroundColor="#00000000"/>
        <style xml:id="s3" tts:backgroundColor="[bogus value]"/>
    </styling>
</head>
<body style="s1 s3 style_bbc_ok">
<div style="s2"><p xml:id="d1" style="s1"><span style="s1">text</span></p></div>
<div style="s2" tts:backgroundColor="#ff0000"><p xml:id="d2"><span style="s1"></span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        vr = ValidationLogger()
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr = ValidationLogger()
        valid = stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_error_results = [
            ValidationResult(
                status=ERROR,
                location='body element '
                         '{http://www.w3.org/ns/ttml#styling}backgroundColor '
                         'attribute',
                message='backgroundColor attribute '
                        '[bogus value] '
                        'is not valid',
                code=ValidationCode.ttml_attribute_styling_attribute
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml#styling}backgroundColor '
                         'styling attribute with value "[bogus value]"',
                message='Value has invalid format',
                code=ValidationCode.ttml_attribute_styling_attribute
            ),
            ValidationResult(
                status=ERROR,
                location='p element {http://www.w3.org/ns/ttml#styling}'
                         'backgroundColor attribute',
                message='backgroundColor #000000 '
                        'is not transparent (BBC requirement)',
                code=ValidationCode.bbc_block_backgroundColor_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='div element {http://www.w3.org/ns/ttml#styling}'
                         'backgroundColor attribute',
                message='backgroundColor #ff0000 '
                        'is not transparent (BBC requirement)',
                code=ValidationCode.bbc_block_backgroundColor_constraint
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
    xmlns:ebutts="urn:ebu:tt:style"
    xmlns:itts="http://www.w3.org/ns/ttml/profile/imsc1#styling"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="style_bbc_ok"
        tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
        ebutts:linePadding="0.5c" itts:fillLineGap="true" tts:color="#ffffff"/>
        <style xml:id="span_background" tts:backgroundColor="#000000"/>
    </styling>
</head>
<body style="style_bbc_ok">
<div><p xml:id="d1" style="s1"><span style="span_background">text</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = ValidationLogger()
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
        vr = ValidationLogger()
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
    xmlns:ebutts="urn:ebu:tt:style"
    xmlns:itts="http://www.w3.org/ns/ttml/profile/imsc1#styling"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="style_bbc_ok"
        tts:fontFamily="jelly, ice cream, default"
        ebutts:linePadding="0.5c" itts:fillLineGap="true"
        tts:color="#ffffff"/>
        <style xml:id="span_background" tts:backgroundColor="#000000"/>
    </styling>
</head>
<body style="style_bbc_ok">
<div><p xml:id="d1" style="style_bbc_ok"><span style="span_background">text</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = ValidationLogger()
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
        vr = ValidationLogger()
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
                        "differs from BBC requirement",
                code=ValidationCode.bbc_text_fontFamily_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='span element xml:id omitted',
                message="Computed fontFamily "
                        "['jelly', 'ice cream', 'default'] "
                        "differs from BBC requirement",
                code=ValidationCode.bbc_text_fontFamily_constraint
            ),
        ]
        vr_errors = [r for r in vr if r.status == ERROR]
        self.assertListEqual(
            vr_errors,
            expected_validation_error_results)

    def test_fontSize_ok_landscape(self):
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
        <style xml:id="style_bbc_ok"
        tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
        tts:fontSize="95%" tts:color="#ffffff"/>
        <style xml:id="span_background" tts:backgroundColor="#000000"/>
        <style xml:id="s2" tts:lineHeight="120%" ebutts:linePadding="0.5c" itts:fillLineGap="true"/>
    </styling>
</head>
<body>
<div><p xml:id="d1" style="style_bbc_ok s2"><span style="style_bbc_ok span_background">text</span><span tts:fontSize="115%" style="span_background">big</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = ValidationLogger()
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
        vr = ValidationLogger()
        valid = stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertTrue(valid)

    def test_fontSize_ok_vertical(self):
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
        <style xml:id="style_bbc_ok"
        tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
        tts:fontSize="56%" tts:color="#ffffff"/>
        <style xml:id="span_background" tts:backgroundColor="#000000"/>
        <style xml:id="s2" tts:lineHeight="120%" ebutts:linePadding="0.5c" itts:fillLineGap="true"/>
    </styling>
</head>
<body>
<div><p xml:id="d1" style="style_bbc_ok s2"><span style="span_background">text</span><span tts:fontSize="115%" style="span_background">big</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = ValidationLogger()
        context = {
            "args": {
                "vertical": True
            }
        }
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
        vr = ValidationLogger()
        valid = stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertTrue(valid)

    def test_fontSize_bad_landscape(self):
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
        <style xml:id="fontStyle"
            tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
            ebutts:linePadding="0.5c" itts:fillLineGap="true"/>
        <style xml:id="fontSize1"
            tts:fontSize="75%"/>
        <style xml:id="fontSize2"
            tts:fontSize="200%"/>
        <style xml:id="span_background"
            tts:backgroundColor="#000000ff"/>
    </styling>
</head>
<body style="fontStyle">
<div><p xml:id="d1" style="fontSize1"><span style="fontSize1 span_background">text</span><span tts:fontSize="20%" tts:backgroundColor="#000000">tiny</span></p></div>
<div><p xml:id="d2" style="fontSize2"><span style="fontSize2 span_background" xml:id="sp3">text</span><span xml:id="sp4" tts:fontSize="20%" tts:backgroundColor="#000000">tiny</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = ValidationLogger()
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
        vr = ValidationLogger()
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
                message="Computed fontSize "
                        "5.000rh "
                        "outside BBC-allowed range 6rh-7.5rh",
                code=ValidationCode.bbc_text_fontSize_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='span element xml:id omitted',
                message="Computed fontSize "
                        "3.750rh "
                        "outside BBC-allowed range 6rh-7.5rh",
                code=ValidationCode.bbc_text_fontSize_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='span element xml:id omitted',
                message="Computed fontSize "
                        "1.000rh "
                        "outside BBC-allowed range 6rh-7.5rh",
                code=ValidationCode.bbc_text_fontSize_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='p element xml:id d2',
                message="Computed fontSize "
                        "13.333rh "
                        "outside BBC-allowed range 6rh-7.5rh",
                code=ValidationCode.bbc_text_fontSize_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='span element xml:id sp3',
                message="Computed fontSize "
                        "26.667rh "
                        "outside BBC-allowed range 6rh-7.5rh",
                code=ValidationCode.bbc_text_fontSize_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='span element xml:id sp4',
                message="Computed fontSize "
                        "2.667rh "
                        "outside BBC-allowed range 6rh-7.5rh",
                code=ValidationCode.bbc_text_fontSize_constraint
            ),
        ]
        vr_errors = [r for r in vr if r.status == ERROR]
        self.assertListEqual(
            vr_errors,
            expected_validation_error_results)

    def test_fontSize_bad_vertical(self):
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
        <style xml:id="fontStyle"
            tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
            ebutts:linePadding="0.5c" itts:fillLineGap="true"/>
        <style xml:id="fontSize1"
            tts:fontSize="75%"/>
        <style xml:id="fontSize2"
            tts:fontSize="200%"/>
        <style xml:id="span_background"
            tts:backgroundColor="#000000ff"/>
    </styling>
</head>
<body style="fontStyle">
<div><p xml:id="d1" style="fontSize1"><span style="fontSize1 span_background">text</span><span tts:fontSize="20%" tts:backgroundColor="#000000">tiny</span></p></div>
<div><p xml:id="d2" style="fontSize2"><span style="fontSize2 span_background" xml:id="sp3">text</span><span xml:id="sp4" tts:fontSize="20%" tts:backgroundColor="#000000">tiny</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = ValidationLogger()
        context = {
            "args": {
                "vertical": True
            }
        }
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
        vr = ValidationLogger()
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
                message="Computed fontSize "
                        "5.000rh "
                        "outside BBC-allowed range 3rh-4.5rh",
                code=ValidationCode.bbc_text_fontSize_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='span element xml:id omitted',
                message="Computed fontSize "
                        "1.000rh "
                        "outside BBC-allowed range 3rh-4.5rh",
                code=ValidationCode.bbc_text_fontSize_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='p element xml:id d2',
                message="Computed fontSize "
                        "13.333rh "
                        "outside BBC-allowed range 3rh-4.5rh",
                code=ValidationCode.bbc_text_fontSize_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='span element xml:id sp3',
                message="Computed fontSize "
                        "26.667rh "
                        "outside BBC-allowed range 3rh-4.5rh",
                code=ValidationCode.bbc_text_fontSize_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='span element xml:id sp4',
                message="Computed fontSize "
                        "2.667rh "
                        "outside BBC-allowed range 3rh-4.5rh",
                code=ValidationCode.bbc_text_fontSize_constraint
            ),
        ]
        vr_errors = [r for r in vr if r.status == ERROR]
        self.assertListEqual(
            vr_errors,
            expected_validation_error_results)

    def test_lineHeight_bad(self):
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
        <style xml:id="fontStyle"
            tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
            tts:fontSize="112.5%" ebutts:linePadding="0.5c" itts:fillLineGap="true"/>
        <style xml:id="lineHeight1"
            tts:lineHeight="120%"/>
        <style xml:id="lineHeight2"
            tts:lineHeight="121%"/>
        <style xml:id="span_background"
            tts:backgroundColor="#000000ff"/>
    </styling>
</head>
<body style="fontStyle">
<div><p xml:id="d1" style="lineHeight1"><span style="span_background">text</span></p></div>
<div><p xml:id="d2" style="lineHeight2"><span style="span_background" xml:id="sp3">text</span></p></div>
<div><p xml:id="d3" style="lineHeight1" tts:fontSize="9%"><span style="span_background" xml:id="sp4">text</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = ValidationLogger()
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
        vr.clear()
        valid = stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_error_results = [
            ValidationResult(
                status=ERROR,
                location='p element xml:id d2',
                message='Computed lineHeight 9.075rh outside '
                        'BBC-allowed range 7.200rh-9.000rh',
                code=ValidationCode.bbc_text_lineHeight_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='p element xml:id d3',
                message='Computed fontSize 0.675rh outside '
                        'BBC-allowed range 6rh-7.5rh',
                code=ValidationCode.bbc_text_fontSize_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='p element xml:id d3',
                message='Computed lineHeight 0.810rh outside '
                        'BBC-allowed range 7.200rh-9.000rh',
                code=ValidationCode.bbc_text_lineHeight_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='span element xml:id sp4',
                message='Computed fontSize 0.675rh outside '
                        'BBC-allowed range 6rh-7.5rh',
                code=ValidationCode.bbc_text_fontSize_constraint
            ),
        ]
        vr_errors = [r for r in vr if r.status == ERROR]
        self.assertListEqual(
            vr_errors,
            expected_validation_error_results)

    def test_multiRowAlign(self):
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
        <style xml:id="style_bbc_ok"
        tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
        tts:fontSize="95%" tts:lineHeight="120%"
        ebutts:linePadding="0.5c" itts:fillLineGap="true"/>
        <style xml:id="span_background" tts:backgroundColor="#000000"/>
        <style xml:id="mra_center" ebutts:multiRowAlign="center"/>
        <style xml:id="ta_center" tts:textAlign="center"/>
        <style xml:id="ta_right" tts:textAlign="right"/>
    </styling>
</head>
<body>
<div>
<p xml:id="d1" style="style_bbc_ok"><span style="span_background">text</span></p>
<p xml:id="d2" style="style_bbc_ok mra_center ta_center"><span style="span_background">text</span></p>
<p xml:id="d3" style="style_bbc_ok mra_center ta_right"><span style="span_background">text</span></p>
</div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = ValidationLogger()
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
        vr = ValidationLogger()
        valid = stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )

        self.assertTrue(valid)

        expected_validation_results = [
            ValidationResult(
                status=INFO,
                location='p element xml:id d2',
                message="Computed multiRowAlign set to "
                        "center, matches textAlign",
                code=ValidationCode.ebuttd_multiRowAlign
            ),
            ValidationResult(
                status=WARN,
                location='p element xml:id d3',
                message="Computed multiRowAlign set to "
                        "center, differs from textAlign "
                        "right (Not expected in BBC "
                        "requirements)",
                code=ValidationCode.bbc_text_multiRowAlign_constraint
            ),
        ]
        vr_mra = [r for r in vr if 'multiRowAlign' in r.message]
        self.assertListEqual(
            vr_mra,
            expected_validation_results)

    def test_linePadding(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ebutts="urn:ebu:tt:style"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="s1"
        tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
        tts:fontSize="75%" tts:lineHeight="120%"/>
        <style xml:id="lp_toosmall" ebutts:linePadding="0.1c"/>
        <style xml:id="lp_good" ebutts:linePadding="0.5c"/>
        <style xml:id="lp_toobig" ebutts:linePadding="10c"/>
    </styling>
</head>
<body>
<div>
<p xml:id="d1" style="s1"><span>text no linepadding</span></p>
<p xml:id="d2" style="s1 lp_toosmall"><span>linepadding too small</span></p>
<p xml:id="d3" style="s1 lp_toobig"><span>linepadding too big</span></p>
<p xml:id="d4" style="s1 lp_good"><span>linepadding just right</span></p>
</div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = ValidationLogger()
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
        vr = ValidationLogger()
        valid = stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )

        self.assertFalse(valid)

        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='p element xml:id d1',
                message="Computed linePadding 0c "
                        "outside BBC-allowed range",
                code=ValidationCode.bbc_text_linePadding_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='p element xml:id d2',
                message="Computed linePadding 0.1c "
                        "outside BBC-allowed range",
                code=ValidationCode.bbc_text_linePadding_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='p element xml:id d3',
                message="Computed linePadding 10c "
                        "outside BBC-allowed range",
                code=ValidationCode.bbc_text_linePadding_constraint
            ),
            ValidationResult(
                status=GOOD,
                location='p element xml:id d4',
                message="Computed linePadding 0.5c "
                        "within BBC-allowed range",
                code=ValidationCode.bbc_text_linePadding_constraint
            ),
        ]
        vr_lp = [r for r in vr if 'linePadding' in r.message]
        self.assertListEqual(
            vr_lp,
            expected_validation_results)

    def test_fillLineGap(self):
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
        tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
        tts:fontSize="75%" tts:lineHeight="120%" ebutts:linePadding="0.5c"/>
        <style xml:id="flg_false" itts:fillLineGap="false"/>
        <style xml:id="flg_true" itts:fillLineGap="true"/>
    </styling>
</head>
<body>
<div>
<p xml:id="d1" style="s1"><span>text no fillLineGap</span></p>
<p xml:id="d2" style="s1 flg_false"><span>fillLineGap false</span></p>
<p xml:id="d3" style="s1 flg_true"><span>fillLineGap true</span></p>
</div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = ValidationLogger()
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
        vr = ValidationLogger()
        valid = stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )

        self.assertFalse(valid)

        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='p element xml:id d1',
                message="Computed fillLineGap false "
                        "not BBC-allowed value",
                code=ValidationCode.bbc_text_fillLineGap_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='p element xml:id d2',
                message="Computed fillLineGap false "
                        "not BBC-allowed value",
                code=ValidationCode.bbc_text_fillLineGap_constraint
            ),
        ]
        vr_lp = [r for r in vr if 'fillLineGap' in r.message]
        self.assertListEqual(
            vr_lp,
            expected_validation_results)

    def test_colors_ok(self):
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
        tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
        tts:fontSize="100%" tts:lineHeight="120%" ebutts:linePadding="0.5c"
        itts:fillLineGap="true"/>
        <style xml:id="span_background" tts:backgroundColor="#000000"/>
        <style xml:id="white" tts:color="#ffffff"/>
        <style xml:id="yellow" tts:color="#ffff00FF"/>
        <style xml:id="green" tts:color="#00ff00"/>
        <style xml:id="cyan" tts:color="#00FFFF"/>
    </styling>
</head>
<body>
<div style="s1">
<p xml:id="d1"><span style="span_background">text default colour</span></p>
<p xml:id="d2" style="s1 white"><span style="span_background">white</span></p>
<p xml:id="d3"><span style="yellow span_background">yellow</span></p>
<p xml:id="d4"><span style="green span_background">green</span></p>
<p xml:id="d5"><span style="cyan span_background">cyan</span></p>
</div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = ValidationLogger()
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
        vr = ValidationLogger()
        valid = stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )

        self.assertTrue(valid)

        expected_validation_results = [
        ]
        vr_lp = [r for r in vr if 'color' in r.message]
        self.assertListEqual(
            vr_lp,
            expected_validation_results)

    def test_colors_bad(self):
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
        tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
        tts:fontSize="75%" tts:lineHeight="120%" ebutts:linePadding="0.5c"
        itts:fillLineGap="true" tts:color="#ffffff"/>
        <style xml:id="span_background_1" tts:backgroundColor="#00000080"/>
        <style xml:id="span_background_2" tts:backgroundColor="#ffffff00"/>
        <style xml:id="span_background_3" tts:backgroundColor="#ffff00ff"/>
        <style xml:id="blue" tts:color="#0000ff"/>
        <style xml:id="lime" tts:color="#00ff00ff"/>
        <style xml:id="reddish" tts:color="#99111180"/>
    </styling>
</head>
<body>
<div style="s1">
<p xml:id="d1"><span>text no background colour</span></p>
<p xml:id="d2" style="blue"><span style="span_background_1">blue</span></p>
<p xml:id="d3"><span style="reddish span_background_2">reddish</span></p>
<p xml:id="d4"><span style="lime span_background_3">lime</span></p>
</div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = ValidationLogger()
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
        vr = ValidationLogger()
        valid = stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )

        self.assertFalse(valid)

        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='span element xml:id omitted',
                message="Computed backgroundColor #00000000 "
                        "not BBC-allowed value",
                code=ValidationCode.bbc_text_backgroundColor_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='span element xml:id omitted',
                message="Computed color #0000ff "
                        "not BBC-allowed value",
                code=ValidationCode.bbc_text_color_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='span element xml:id omitted',
                message="Computed backgroundColor #00000080 "
                        "not BBC-allowed value",
                code=ValidationCode.bbc_text_backgroundColor_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='span element xml:id omitted',
                message="Computed color #99111180 "
                        "not BBC-allowed value",
                code=ValidationCode.bbc_text_color_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='span element xml:id omitted',
                message="Computed backgroundColor #ffffff00 "
                        "not BBC-allowed value",
                code=ValidationCode.bbc_text_backgroundColor_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='span element xml:id omitted',
                message="Computed backgroundColor #ffff00ff "
                        "not BBC-allowed value",
                code=ValidationCode.bbc_text_backgroundColor_constraint
            ),
        ]
        vr_lp = [r for r in vr
                 if 'color' in r.message or 'backgroundColor' in r.message]
        self.assertListEqual(
            vr_lp,
            expected_validation_results)

    def test_fontStyle(self):
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
        tts:fontFamily="ReithSans, Arial, Roboto, proportionalSansSerif, default"
        tts:fontSize="95%" tts:lineHeight="120%" ebutts:linePadding="0.5c"
        itts:fillLineGap="true"/>
        <style xml:id="span_background" tts:backgroundColor="#000000"/>
        <style xml:id="fs_normal" tts:fontStyle="normal"/>
        <style xml:id="fs_italic" tts:fontStyle="italic"/>
    </styling>
</head>
<body>
<div style="s1">
<p xml:id="d1"><span style="span_background">text default fontStyle</span></p>
<p xml:id="d2"><span style="span_background fs_normal">also normal</span></p>
<p xml:id="d3"><span style="span_background fs_italic">italic</span></p>
</div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck(
            sub_checks=[
                stylingCheck.stylingCheck(),
                layoutCheck.layoutCheck(),
            ]
        )
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = ValidationLogger()
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
        vr = ValidationLogger()
        valid = stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )

        self.assertTrue(valid)

        expected_validation_results = [
            ValidationResult(
                status=WARN,
                location='span element xml:id omitted',
                message='Computed fontStyle italic not in general use for BBC',
                code=ValidationCode.bbc_text_fontStyle_constraint
                )
            ]
        vr_lp = [r for r in vr if 'fontStyle' in r.message]
        self.assertListEqual(
            vr_lp,
            expected_validation_results)
