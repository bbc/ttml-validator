import unittest
import src.xmlChecks.timingXmlCheck as timingXmlCheck
import xml.etree.ElementTree as ElementTree
from src.validationResult import ValidationResult, ERROR, GOOD, WARN, INFO


class testTimingXmlCheck(unittest.TestCase):
    maxDiff = None

    ##################################
    #  Timing tests                  #
    ##################################

    def test_timingCheck_no_times(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p1"><span>content here</span></p>
<p xml:id="p2"><span>content here</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        timingCheck = timingXmlCheck.timingCheck()
        vr = []
        context = {}
        valid = timingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 0s, end of doc is undefined'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timingCheck_ok_p_times_no_gaps(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p1" begin="00:00:01.234" end="00:00:02"><span>content here</span></p>
<p xml:id="p2" begin="00:00:02.0" end="00:00:03.4"><span>content here</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        timingCheck = timingXmlCheck.timingCheck()
        vr = []
        context = {}
        valid = timingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 1.234s, end of doc is 3.4s'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timingCheck_ok_span_times_no_gaps(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p1"><span begin="00:00:01.234" end="00:00:02">content here</span></p>
<p xml:id="p2"><span begin="00:00:02.0" end="00:00:03.4">content here</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        timingCheck = timingXmlCheck.timingCheck()
        vr = []
        context = {}
        valid = timingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 1.234s, end of doc is 3.4s'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timingCheck_bad_p_time_expressions_no_gaps(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p1" begin="1.234s" end="2s"><span>content here</span></p>
<p xml:id="p2" begin="50f" end="00:00:03.4"><span>content here</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        timingCheck = timingXmlCheck.timingCheck()
        vr = []
        context = {}
        valid = timingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}p element xml:id p1',
                message='begin=1.234s is not a valid offset time'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}p element xml:id p1',
                message='end=2s is not a valid offset time'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}p element xml:id p2',
                message='begin=50f is not a valid offset time'
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 1.234s, end of doc is 3.4s'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timingCheck_bad_span_time_expressions_no_gaps(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p1"><span begin="1.234s" end="2s">content here</span></p>
<p xml:id="p2"><span begin="50f" end="00:00:03.4">content here</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        timingCheck = timingXmlCheck.timingCheck()
        vr = []
        context = {}
        valid = timingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}span element xml:id omitted',
                message='begin=1.234s is not a valid offset time'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}span element xml:id omitted',
                message='end=2s is not a valid offset time'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}span element xml:id omitted',
                message='begin=50f is not a valid offset time'
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 1.234s, end of doc is 3.4s'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timingCheck_ok_p_times_gaps(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p1" begin="00:00:01.234" end="00:00:02"><span>content here</span></p>
<p xml:id="p2" begin="00:00:02.1" end="00:00:03.4"><span>content here</span></p>
<p xml:id="p3" begin="00:00:04.2" end="00:00:05.4"><span>content here</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        timingCheck = timingXmlCheck.timingCheck()
        vr = []
        context = {}
        valid = timingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='Gap from 2.0s to 2.1s',
                message='Non-zero gap between subtitles is shorter than 0.8s'
            ),
            ValidationResult(
                status=WARN,
                location='Gap from 3.4s to 4.2s',
                message='Short gap between subtitles should be '
                        'at least 1.5s'
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 1.234s, end of doc is 5.4s'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timingCheck_ok_span_times_gaps(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p1"><span begin="00:00:01.234" end="00:00:02">content here</span></p>
<p xml:id="p2"><span begin="00:00:02.2" end="00:00:03.4">content here</span></p>
<p xml:id="p3" begin="00:00:04.3"><span end="00:00:06.4">content here</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        timingCheck = timingXmlCheck.timingCheck()
        vr = []
        context = {}
        valid = timingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='Gap from 2.0s to 2.2s',
                message='Non-zero gap between subtitles is shorter than 0.8s'
            ),
            ValidationResult(
                status=WARN,
                location='Gap from 3.4s to 4.3s',
                message='Short gap between subtitles should be '
                        'at least 1.5s'
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 1.234s, end of doc is 10.7s'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timingCheck_not_enough_early_subs_p_times(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p1" begin="00:00:01.234" end="00:00:02"><span>early content here</span></p>
<p xml:id="p2" begin="00:23:00" end="00:23:03.4"><span>late content here</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        timingCheck = timingXmlCheck.timingCheck()
        vr = []
        context = {}
        valid = timingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='p elements beginning before 00:23:00.000',
                message='1 subtitle(s) found, minimum 2 required'
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 1.234s, end of doc is 1383.4s'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timingCheck_not_enough_early_subs_span_times(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p1"><span begin="00:00:01.234" end="00:00:02">early content here</span></p>
<p xml:id="p2"><span begin="00:23:00" end="00:23:03.4">late content here</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        timingCheck = timingXmlCheck.timingCheck()
        vr = []
        context = {}
        valid = timingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='p elements beginning before 00:23:00.000',
                message='1 subtitle(s) found, minimum 2 required'
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 1.234s, end of doc is 1383.4s'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)
