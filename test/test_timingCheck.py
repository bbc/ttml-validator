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

    def test_timingCheck_subs_overlap_segment(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p1" begin="00:06:20.0" end="00:06:24.001"><span>just overlaps the beginning</span></p>
<p xml:id="p2"><span begin="00:06:27.83" end="00:06:30.4">just overlaps the end</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        timingCheck = timingXmlCheck.timingCheck(
            epoch=384,
            segment_dur=3.84,
            segment_relative_timing=False)
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
                message='Skipping check for enough early subtitles because '
                        'segment duration is shorter than search period.'
            ),
            ValidationResult(
                status=GOOD,
                location='Timed content',
                message='Document content overlaps the segment '
                        'interval [384s..387.84s)'
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 380.0s, end of doc is 390.4s'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timingCheck_subs_wholly_within_segment(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p begin="00:06:24.5" end="00:06:25.5" xml:id="p1"><span>within the segment 1</span></p>
<p begin="00:06:25.500" end="00:06:27" xml:id="p2"><span>within the segment 2</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        timingCheck = timingXmlCheck.timingCheck(
            epoch=384,
            segment_dur=3.84,
            segment_relative_timing=False)
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
                message='Skipping check for enough early subtitles because '
                        'segment duration is shorter than search period.'
            ),
            ValidationResult(
                status=GOOD,
                location='Timed content',
                message='Document content overlaps the segment '
                        'interval [384s..387.84s)'
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 384.5s, end of doc is 387.0s'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timingCheck_empty_doc_within_segment(self):
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
                status=WARN,
                location='{http://www.w3.org/ns/ttml}tt element',
                message='No body element found, skipping timing tests'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timingCheck_subs_end_before_segment(self):
        # TODO
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p begin="00:06:20.5" end="00:06:21.0" xml:id="p1"><span>within the segment 1</span></p>
<p begin="00:06:22.500" end="00:06:24.0" xml:id="p2"><span>within the segment 2</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        timingCheck = timingXmlCheck.timingCheck(
            epoch=384,
            segment_dur=3.84,
            segment_relative_timing=False)
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
                status=INFO,
                location='Document',
                message='Skipping check for enough early subtitles because '
                        'segment duration is shorter than search period.'
            ),
            ValidationResult(
                status=ERROR,
                location='Timed content',
                message='Document content is timed outside the segment '
                        'interval [384s..387.84s)'
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 380.5s, end of doc is 384.0s'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timingCheck_subs_begin_after_segment(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p begin="00:06:27.841" end="00:06:28.5" xml:id="p1"><span>after the segment 1</span></p>
<p begin="00:06:28.500" end="00:06:30" xml:id="p2"><span>after the segment 2</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        timingCheck = timingXmlCheck.timingCheck(
            epoch=384,
            segment_dur=3.84,
            segment_relative_timing=False)
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
                status=INFO,
                location='Document',
                message='Skipping check for enough early subtitles because '
                        'segment duration is shorter than search period.'
            ),
            ValidationResult(
                status=ERROR,
                location='Timed content',
                message='Document content is timed outside the segment '
                        'interval [384s..387.84s)'
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 387.841s, end of doc is 390.0s'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)
