import unittest
import src.xmlChecks.bodyXmlCheck as bodyXmlCheck
from src.xmlChecks.timingAttributeCheck import noNestedTimedElementsCheck, \
    noTimingAttributeCheck
from src.xmlChecks.divXmlCheck import divCheck
from src.xmlChecks.pXmlCheck import pCheck
from src.xmlChecks.spanXmlCheck import spanCheck
from src.xmlChecks.xmlIdCheck import requireXmlId
from src.xmlChecks.textCheck import noTextChildren, checkLineBreaks
import xml.etree.ElementTree as ElementTree
from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationResult import ValidationResult, \
    ERROR, GOOD, WARN, INFO


class testBodyXmlCheck(unittest.TestCase):
    maxDiff = None

    ##################################
    #  Body tests                    #
    ##################################

    def setUp(self) -> None:
        self.bodyCheck = bodyXmlCheck.bodyCheck(
            sub_checks=[
                noTimingAttributeCheck(),
                divCheck(sub_checks=[
                    noTimingAttributeCheck(),
                    pCheck(sub_checks=[
                        requireXmlId(),
                        noTextChildren(),
                        checkLineBreaks(),
                        spanCheck(sub_checks=[
                            noNestedTimedElementsCheck()
                            ],
                            require_text_in_span=True,
                            permit_nested_spans=False)
                        ])
                    ])
                ])
        return super().setUp()

    def test_bodyCheck_ok(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div><p xml:id="p1"><span>content here</span></p></div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        vr = ValidationLogger()
        context = {}
        valid = self.bodyCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt/'
                         '{http://www.w3.org/ns/ttml}body',
                message='Body checked',
                code=ValidationCode.ttml_element_body
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_bodyCheck_no_body(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        vr = ValidationLogger()
        context = {}
        valid = self.bodyCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=INFO,
                location='{http://www.w3.org/ns/ttml}tt/'
                         '{http://www.w3.org/ns/ttml}body',
                message='No body elements present: empty document',
                code=ValidationCode.ttml_element_body
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt/'
                         '{http://www.w3.org/ns/ttml}body',
                message='Body checked',
                code=ValidationCode.ttml_element_body
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_bodyCheck_too_many_body(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div><p xml:id="p1"><span>content here</span></p></div></body>
<body/>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        vr = ValidationLogger()
        context = {}
        valid = self.bodyCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}tt/'
                         '{http://www.w3.org/ns/ttml}body',
                message='Found 2 body elements, expected 1',
                code=ValidationCode.ttml_element_body
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_bodyCheck_no_div(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body/>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        vr = ValidationLogger()
        context = {}
        valid = self.bodyCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}body/'
                         '{http://www.w3.org/ns/ttml}div',
                message='Found 0 div elements, require >0',
                code=ValidationCode.ebuttd_empty_body_constraint
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_bodyCheck_nested_div_missing_p(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body>
  <div>
    <div><p xml:id="p1"><span/></p>
      <div><p xml:id="p2"><span/></p></div>
    </div>
    <div/>
  </div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        vr = ValidationLogger()
        context = {}
        valid = self.bodyCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div/'
                         '{http://www.w3.org/ns/ttml}div',
                message='Found 2 div children of a div, require 0',
                code=ValidationCode.ebuttd_nested_div_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div/'
                         '{http://www.w3.org/ns/ttml}div',
                message='Found 1 div children of a div, require 0',
                code=ValidationCode.ebuttd_nested_div_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div/'
                         '{http://www.w3.org/ns/ttml}p xml:id omitted',
                message='Found 0 p children of a div, require >0',
                code=ValidationCode.ebuttd_empty_div_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div/'
                         '{http://www.w3.org/ns/ttml}p xml:id omitted',
                message='Found 0 p children of a div, require >0',
                code=ValidationCode.ebuttd_empty_div_constraint
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_p_no_xml_id(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p1"><span>p1 content here</span></p>
<p><span>content here</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        vr = ValidationLogger()
        context = {}
        valid = self.bodyCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='p xml:id omitted',
                message='Element missing required xml:id attribute',
                code=ValidationCode.ebuttd_p_xml_id_constraint
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_p_with_text_children(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p1">Bad<span>p1 content here</span>Bad 2<span>OK</span>Bad 3</p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        vr = ValidationLogger()
        context = {}
        valid = self.bodyCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}p element xml:id p1',
                message='Text content found in prohibited location.',
                code=ValidationCode.bbc_text_span_constraint
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_p_no_span_children(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p1"></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        vr = ValidationLogger()
        context = {}
        valid = self.bodyCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}p'
                         '/{http://www.w3.org/ns/ttml}span xml:id p1',
                message='Found 0 span elements; '
                        'text content needs to be in a styled span',
                code=ValidationCode.bbc_text_span_constraint
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_p_line_breaks_no_brs(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p0"><span>p0 content here with no line break</span></p>
<p xml:id="p1"><span>p1 content here
with bad line break</span></p>
<p xml:id="p2"><span>p2 content here<br/>with good line break</span></p>
<p xml:id="p3"><span>p3 content here</span><br/><span>with good line break</span></p>
<p xml:id="p4"><span>p4 content here
<br/>
with good line break</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        vr = ValidationLogger()
        context = {}
        valid = self.bodyCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=WARN,
                location='{http://www.w3.org/ns/ttml}p element xml:id p1',
                message='Text content contains line breaks '
                        'but no <br> elements.',
                code=ValidationCode.ttml_element_br
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt/'
                         '{http://www.w3.org/ns/ttml}body',
                message='Body checked',
                code=ValidationCode.ttml_element_body
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_nested_span(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p1"><span>p1 content here</span></p>
<p xml:id="p2"><span>content <span>not allowed</span> here</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        vr = ValidationLogger()
        context = {}
        valid = self.bodyCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}span/'
                         '{http://www.w3.org/ns/ttml}span xml:id omitted',
                message='Found 1 span element children of span, require 0',
                code=ValidationCode.ebuttd_nested_span_constraint
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timing_on_body_and_div(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body begin="00:00:01" dur="00:01:00">
<div end="00:00:30.123" xml:id="div_end">
<p xml:id="p1"><span>p1 content here</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        vr = ValidationLogger()
        context = {}
        valid = self.bodyCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}body element '
                         'xml:id omitted',
                message='Prohibited timing attributes '
                        '[\'begin\', \'dur\'] present',
                code=ValidationCode.ebuttd_timing_attribute_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div element '
                         'xml:id div_end',
                message='Prohibited timing attributes '
                        '[\'end\'] present',
                code=ValidationCode.ebuttd_timing_attribute_constraint
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timing_on_p_and_descendant_span(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body>
<div xml:id="div_end">
<p xml:id="p1" begin="00:00:01"><span end="00:00:30.123">p1 content here</span></p>
<p xml:id="p2" begin="00:01:01" dur="00:01:00"><span>p1 <span end="00:00:30.123">content </span> here</span></p>
<p xml:id="p3"><span begin="00:02:01" dur="00:01:00">p1 <span end="00:00:30.123">content </span> here</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        vr = ValidationLogger()
        context = {}
        valid = self.bodyCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}span element',
                message='Nested elements with timing attributes prohibited',
                code=ValidationCode.ebuttd_nested_timing_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}span/'
                         '{http://www.w3.org/ns/ttml}span xml:id omitted',
                message='Found 1 span element children of span, require 0',
                code=ValidationCode.ebuttd_nested_span_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}span element',
                message='Nested elements with timing attributes prohibited',
                code=ValidationCode.ebuttd_nested_timing_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}span/'
                         '{http://www.w3.org/ns/ttml}span xml:id omitted',
                message='Found 1 span element children of span, require 0',
                code=ValidationCode.ebuttd_nested_span_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}span element',
                message='Nested elements with timing attributes prohibited',
                code=ValidationCode.ebuttd_nested_timing_constraint
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)
