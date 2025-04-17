import unittest
import src.xmlChecks.regionRefsCheck as regionRefsCheck
import src.xmlChecks.styleRefsCheck as styleRefsCheck
import src.xmlChecks.headXmlCheck as headXmlCheck
import xml.etree.ElementTree as ElementTree
from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationResult import ValidationResult, \
    ERROR, GOOD, WARN


class testRegionRefsCheck(unittest.TestCase):
    maxDiff = None

    def test_region_refs_ok(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:ebutts="urn:ebu:tt:style"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <styling>
        <style xml:id="s_region" ebutts:linePadding="0.5c"/>
        <style xml:id="s1" tts:color="#ffffffff"/>
    </styling>
    <layout>
        <region xml:id="r1"
            tts:origin="10% 10%"
            tts:extent="80% 80%"
            tts:displayAlign="after"
            tts:overflow="visible"
            tts:writingMode="lrtb"
            style="s_region"/>
    </layout>
</head>
<body style="s1" region="r1">
<div><p xml:id="p1"/></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        regionsCheck = regionRefsCheck.regionRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        vr = ValidationLogger()
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr = ValidationLogger()
        valid = regionsCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=WARN,
                location='region element xml:id r1',
                message='Non-permitted style attribute '
                        '{urn:ebu:tt:style}linePadding present on '
                        'region element - presentation may differ from '
                        'expectation',
                code=ValidationCode.ttml_attribute_styling_attribute
            ),
            ValidationResult(
                status=GOOD,
                location='document',
                message='Region references and attributes checked',
                code=ValidationCode.ttml_layout_region_association
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_region_refs_unref_region(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <layout>
        <region xml:id="r1"
            tts:origin="10% 10%"
            tts:extent="80% 80%"
            tts:displayAlign="after"
            tts:overflow="visible"/>
    </layout>
</head>
<body/>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        regionsCheck = regionRefsCheck.regionRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        vr = ValidationLogger()
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr.clear()
        # since there's no styling in the stimulus, there's
        # no id_to_style_attribs_map, but that causes a region
        # text skip later, so insert one manually.
        context['id_to_style_attribs_map'] = {}
        valid = regionsCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=WARN,
                location='region element xml:id r1',
                message='Unreferenced region element',
                code=ValidationCode.ttml_element_region
            ),
            ValidationResult(
                status=GOOD,  # Should this be reported in this test case?
                location='document',
                message='Region references and attributes checked',
                code=ValidationCode.ttml_layout_region_association
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_region_content_pruned(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
    <ttm:copyright>valid"</ttm:copyright>
    <layout>
        <region xml:id="r1"
            tts:origin="10% 10%"
            tts:extent="80% 30%"
            tts:displayAlign="after"
            tts:overflow="visible"/>
        <region xml:id="r2"
            tts:origin="10% 60%"
            tts:extent="80% 30%"
            tts:displayAlign="after"
            tts:overflow="visible"/>
    </layout>
</head>
<body>
<div region="r1"><p>ok content</p><p region="r2">pruned</p></div>
<div region="r1"><p xml:id="p2">ok content</p><p region="p2">pruned</p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        regionsCheck = regionRefsCheck.regionRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        vr = ValidationLogger()
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr.clear()
        # since there's no styling in the stimulus, there's
        # no id_to_style_attribs_map, but that causes a region
        # text skip later, so insert one manually.
        context['id_to_style_attribs_map'] = {}
        valid = regionsCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=WARN,
                location='region element xml:id r2',
                message='1 elements pruned because their '
                        'ancestor references a different '
                        'region element',
                code=ValidationCode.ttml_layout_region_association
            ),
            ValidationResult(
                status=ERROR,
                location='1 element(s)',
                message='Dropped referenced region p2 does not '
                        'point to a region element',
                code=ValidationCode.ttml_layout_region_association
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_region_refs_ref_not_region(self):
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
    <layout>
        <region xml:id="r1"
            tts:origin="10% 10%"
            tts:extent="80% 80%"
            tts:displayAlign="after"
            tts:overflow="visible"/>
    </layout>
</head>
<body>
<div xml:id="d1" region="not_an_id"></div>
<div xml:id="d2" region="d1"></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        regionsCheck = regionRefsCheck.regionRefsXmlCheck()
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        vr = ValidationLogger()
        context = {}
        # headCheck is a dependency so it populates context['id_to_region_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr.clear()
        valid = regionsCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        # print('\n'+('\n'.join([v.asString() for v in vr])))
        expected_validation_results = [
            ValidationResult(
                status=WARN,
                location='region element xml:id r1',
                message='Unreferenced region element',
                code=ValidationCode.ttml_element_region
            ),
            ValidationResult(
                status=ERROR,
                location='1 element(s)',
                message='Referenced region not_an_id does not '
                        'point to a region element',
                code=ValidationCode.ttml_layout_region_association
            ),
            ValidationResult(
                status=ERROR,
                location='1 element(s)',
                message='Referenced region d1 does not '
                        'point to a region element',
                code=ValidationCode.ttml_layout_region_association
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_region_refs_p_not_in_region(self):
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
        <region xml:id="r1"
            tts:origin="10% 10%"
            tts:extent="80% 80%"
            tts:displayAlign="after"
            tts:overflow="visible"/>
    </layout>
</head>
<body style="s1">
<div region="r1"><p xml:id="p1"/></div>
<div><p xml:id="p2" region="r1"/></div>
<div><p xml:id="p3"/></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        regionsCheck = regionRefsCheck.regionRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        vr = ValidationLogger()
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr.clear()
        valid = regionsCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='1 p element(s)',
                message='Elements not associated with a region',
                code=ValidationCode.ttml_layout_region_association
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_region_refs_missing_required_attrs(self):
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
        <region xml:id="r1"
            tts:extent="80% 80%"
            tts:displayAlign="after"
            tts:overflow="visible"/>
        <region xml:id="r2"
            tts:origin="10% 15.5%"
            tts:displayAlign="after"
            tts:overflow="visible"/>
        <region xml:id="r3"
            tts:origin="10% 10%"
            tts:extent="80% 80%"
            tts:overflow="visible"/>
        <region xml:id="r4"
            tts:origin="10% 10%"
            tts:extent="80% 80%"
            tts:displayAlign="after"/>
    </layout>
</head>
<body style="s1">
<div region="r1"><p xml:id="p1"/></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        regionsCheck = regionRefsCheck.regionRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        vr = ValidationLogger()
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr.clear()
        valid = regionsCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        # print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='region element xml:id r1',
                message='Required style attribute '
                        '{http://www.w3.org/ns/ttml#styling}origin '
                        'missing from region element',
                code=ValidationCode.ebuttd_region_attributes_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='region element xml:id r1',
                message='Region extends out of BBC-defined '
                        'permitted area (9.5%-91.5% horizontally '
                        'and 5%-95% vertically)',
                code=ValidationCode.bbc_region_position_constraint
            ),
            ValidationResult(
                status=WARN,
                location='region element xml:id r2',
                message='Unreferenced region element',
                code=ValidationCode.ttml_element_region
            ),
            ValidationResult(
                status=WARN,
                location='region element xml:id r2',
                message='Required style attribute '
                        '{http://www.w3.org/ns/ttml#styling}extent '
                        'missing from region element',
                code=ValidationCode.ebuttd_region_attributes_constraint
            ),
            ValidationResult(
                status=WARN,
                location='region element xml:id r2',
                message='Region right edge '
                        '110.0% goes beyond 100%',
                code=ValidationCode.ebuttd_region_position_constraint
            ),
            ValidationResult(
                status=WARN,
                location='region element xml:id r2',
                message='Region bottom edge '
                        '115.5% goes beyond 100%',
                code=ValidationCode.ebuttd_region_position_constraint
            ),
            ValidationResult(
                status=WARN,
                location='region element xml:id r2',
                message='Region extends out of BBC-defined '
                        'permitted area (9.5%-91.5% horizontally '
                        'and 5%-95% vertically)',
                code=ValidationCode.bbc_region_position_constraint
            ),
            ValidationResult(
                status=WARN,
                location='region element xml:id r3',
                message='Unreferenced region element',
                code=ValidationCode.ttml_element_region
            ),
            ValidationResult(
                status=WARN,
                location='region element xml:id r3',
                message='Required style attribute '
                        '{http://www.w3.org/ns/ttml#styling}displayAlign '
                        'missing from region element',
                code=ValidationCode.bbc_region_attributes_constraint
            ),
            ValidationResult(
                status=WARN,
                location='region element xml:id r4',
                message='Unreferenced region element',
                code=ValidationCode.ttml_element_region
            ),
            ValidationResult(
                status=WARN,
                location='region element xml:id r4',
                message='Required style attribute '
                        '{http://www.w3.org/ns/ttml#styling}overflow '
                        'missing from region element',
                code=ValidationCode.bbc_region_attributes_constraint
            ),
            ValidationResult(
                status=WARN,
                location='region element xml:id r4',
                message='Region overflow hidden not visible (BBC requirement)',
                code=ValidationCode.bbc_region_overflow_constraint
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_region_bad_backgroundColor(self):
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
        <region xml:id="r1"
            tts:origin="10% 10%"
            tts:extent="80% 80%"
            tts:displayAlign="after"
            tts:overflow="visible"
            tts:backgroundColor="#000000"/>
        <region xml:id="r2"
            tts:origin="10% 10%"
            tts:extent="80% 80%"
            tts:displayAlign="after"
            tts:overflow="visible"
            tts:backgroundColor="#FFFFFFFF"/>
        <region xml:id="r3"
            tts:origin="10% 10%"
            tts:extent="80% 80%"
            tts:displayAlign="after"
            tts:overflow="visible"
            tts:backgroundColor="#abcdef00"/>
    </layout>
</head>
<body style="s1">
<div region="r1"><p xml:id="p1"/></div>
<div region="r2"><p xml:id="p2"/></div>
<div region="r3"><p xml:id="p3"/></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        regionsCheck = regionRefsCheck.regionRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        vr = ValidationLogger()
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr.clear()
        valid = regionsCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        # print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='region element xml:id r1',
                message='backgroundColor value #000000 is non-transparent '
                        'and does not meet BBC requirements',
                code=ValidationCode.bbc_region_backgroundColor_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='region element xml:id r2',
                message='backgroundColor value #FFFFFFFF is non-transparent '
                        'and does not meet BBC requirements',
                code=ValidationCode.bbc_region_backgroundColor_constraint
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_region_bad_style_syntax(self):
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
        <region xml:id="r1"
            tts:origin="10% 10%"
            tts:extent="80px 80px"
            tts:displayAlign="after"
            tts:overflow="visible"/>
    </layout>
</head>
<body style="s1">
<div region="r1"><p xml:id="p1"/></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        stylesCheck = styleRefsCheck.styleRefsXmlCheck()
        regionsCheck = regionRefsCheck.regionRefsXmlCheck()
        headCheck = headXmlCheck.headCheck()
        vr = ValidationLogger()
        context = {}
        # headCheck is a dependency so it populates context['id_to_style_map']
        headCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        stylesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        vr.clear()
        valid = regionsCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml#styling}extent styling '
                         'attribute with value "80px 80px"',
                message='Value has invalid format',
                code=ValidationCode.ttml_attribute_styling_attribute
            ),
            ValidationResult(
                status=ERROR,
                location='region element xml:id r1',
                message='Not got computed values for both origin and extent',
                code=ValidationCode.ttml_attribute_styling_attribute
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)
