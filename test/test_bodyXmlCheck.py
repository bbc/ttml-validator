import unittest
import src.xmlChecks.bodyXmlCheck as bodyXmlCheck
import xml.etree.ElementTree as ElementTree
from src.validationResult import ValidationResult, ERROR, GOOD, WARN, INFO


class testBodyXmlCheck(unittest.TestCase):
    maxDiff = None

    ##################################
    #  Body tests                    #
    ##################################

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
        bodyCheck = bodyXmlCheck.bodyCheck()
        vr = []
        context = {}
        valid = bodyCheck.run(
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
                message='Body checked'
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
        bodyCheck = bodyXmlCheck.bodyCheck()
        vr = []
        context = {}
        valid = bodyCheck.run(
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
                message='Found 0 body elements, expected 1'
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
        bodyCheck = bodyXmlCheck.bodyCheck()
        vr = []
        context = {}
        valid = bodyCheck.run(
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
                message='Found 2 body elements, expected 1'
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
        bodyCheck = bodyXmlCheck.bodyCheck()
        vr = []
        context = {}
        valid = bodyCheck.run(
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
                message='Found 0 div elements, require >0'
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
        bodyCheck = bodyXmlCheck.bodyCheck()
        vr = []
        context = {}
        valid = bodyCheck.run(
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
                message='Found 2 div children of a div, require 0'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div/'
                         '{http://www.w3.org/ns/ttml}div',
                message='Found 1 div children of a div, require 0'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div/'
                         '{http://www.w3.org/ns/ttml}p xml:id omitted',
                message='Found 0 p children of a div, require >0'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div/'
                         '{http://www.w3.org/ns/ttml}p xml:id omitted',
                message='Found 0 p children of a div, require >0'
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
        bodyCheck = bodyXmlCheck.bodyCheck()
        vr = []
        context = {}
        valid = bodyCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div/'
                         '{http://www.w3.org/ns/ttml}p xml:id omitted',
                message='p element missing required xml:id'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_p_no_text_children(self):
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
        bodyCheck = bodyXmlCheck.bodyCheck()
        vr = []
        context = {}
        valid = bodyCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}p element xml:id p1',
                message='Text content found in prohibited location.'
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
        bodyCheck = bodyXmlCheck.bodyCheck()
        vr = []
        context = {}
        valid = bodyCheck.run(
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
                message='Found 1 span element children of span, require 0'
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
        bodyCheck = bodyXmlCheck.bodyCheck()
        vr = []
        context = {}
        valid = bodyCheck.run(
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
                        '{\'begin\', \'dur\'} present'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div element '
                         'xml:id div_end',
                message='Prohibited timing attributes '
                        '{\'end\'} present'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)
