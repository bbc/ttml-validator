# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

import unittest
import src.xmlChecks.headXmlCheck as headXmlCheck
import src.xmlChecks.stylingCheck as stylingCheck
import src.xmlChecks.layoutCheck as layoutCheck
import src.xmlChecks.regionRefsCheck as regionRefsCheck
import src.xmlChecks.styleRefsCheck as styleRefsCheck
import src.xmlChecks.daptTimingXmlCheck as daptTimingXmlCheck
import xml.etree.ElementTree as ElementTree
from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationResult import ValidationResult, \
    ERROR, GOOD, WARN, INFO, SKIP


class testDaptTimingXmlCheck(unittest.TestCase):
    maxDiff = None

    ##################################
    #  Timing tests                  #
    ##################################

    def test_daptTimingCheck_no_times(self):
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
        daptTimingCheck = daptTimingXmlCheck.daptTimingCheck()
        vr = ValidationLogger()
        context = {}
        valid = daptTimingCheck.run(
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
                message='First text appears at 0s, end of doc is undefined',
                code=ValidationCode.ttml_document_timing
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_daptTimingCheck_ok_p_times(self):
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
        daptTimingCheck = daptTimingXmlCheck.daptTimingCheck()
        vr = ValidationLogger()
        context = {}
        valid = daptTimingCheck.run(
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
                message='First text appears at 1.234s, end of doc is 3.4s',
                code=ValidationCode.ttml_document_timing
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_daptTimingCheck_ok_span_times(self):
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
        daptTimingCheck = daptTimingXmlCheck.daptTimingCheck()
        vr = ValidationLogger()
        context = {}
        valid = daptTimingCheck.run(
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
                message='First text appears at 1.234s, end of doc is 3.4s',
                code=ValidationCode.ttml_document_timing
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_daptTimingCheck_bad_p_time_expressions_no_framerate(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p1" begin="1.234s" end="00:00:02:00"><span>content here</span></p>
<p xml:id="p2" begin="50f" end="00:00:03.4"><span>content here</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        daptTimingCheck = daptTimingXmlCheck.daptTimingCheck()
        vr = ValidationLogger()
        context = {}
        valid = daptTimingCheck.run(
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
                message='end=00:00:02:00 is not a valid time '
                        'expression',
                code=ValidationCode.dapt_timing_attribute_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}p element xml:id p1',
                message='end attribute 00:00:02:00 uses frames but frame '
                        'rate not specified on tt element',
                code=ValidationCode.dapt_timing_framerate
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}p element xml:id p2',
                message='begin attribute 50f uses frames but frame rate not '
                        'specified on tt element',
                code=ValidationCode.dapt_timing_framerate
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 1.234s, end of doc is 3.4s',
                code=ValidationCode.ttml_document_timing
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_daptTimingCheck_bad_span_time_expressions_no_ticks(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p1"><span begin="1.234s" end="2s" dur="00:00:02,00">content here</span></p>
<p xml:id="p2"><span begin="2t" end="00:00:04.4" dur="00:00:02.00">content here</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        daptTimingCheck = daptTimingXmlCheck.daptTimingCheck()
        vr = ValidationLogger()
        context = {}
        valid = daptTimingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}span element '
                         'xml:id omitted',
                message='dur=00:00:02,00 is not a valid time expression',
                code=ValidationCode.dapt_timing_attribute_constraint
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}span element '
                         'xml:id omitted, dur attribute',
                message='00:00:02,00 is not a recognised time expression',
                code=ValidationCode.ttml_timing_attribute_syntax
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}span element '
                         'xml:id omitted',
                message='begin attribute 2t uses ticks but tick rate not '
                        'specified on tt element',
                code=ValidationCode.dapt_timing_tickrate
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 1.234s, end of doc is 4.0s',
                code=ValidationCode.ttml_document_timing
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_daptTimingCheck_bad_audio_time_expressions(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body><div>
<p xml:id="p1"><span begin="1.234s" dur="00:00:02.00">content
here<audio clipBegin="5s" clipEnd="7s"/></span></p>
<p xml:id="p2"><span begin="3s" end="00:00:04.4" dur="00:00:02.00">content
here<audio clipBegin="100f" clipEnd="1.5z"/></span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        daptTimingCheck = daptTimingXmlCheck.daptTimingCheck()
        vr = ValidationLogger()
        context = {}
        valid = daptTimingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}audio element '
                         'xml:id omitted',
                message='clipBegin attribute 100f uses frames but '
                        'frame rate not specified on tt element',
                code=ValidationCode.dapt_timing_framerate
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}audio element '
                         'xml:id omitted',
                message='clipEnd=1.5z is not a valid time expression',
                code=ValidationCode.dapt_timing_attribute_constraint
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 1.234s, end of doc is 4.4s',
                code=ValidationCode.ttml_document_timing
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_daptTimingCheck_timeContainer(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body timeContainer="par"><div>
<p xml:id="p1" begin="00:00:01.234" end="00:00:02" timeContainer="seq"><span>content here</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        daptTimingCheck = daptTimingXmlCheck.daptTimingCheck()
        vr = ValidationLogger()
        context = {}
        valid = daptTimingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=WARN,
                location='{http://www.w3.org/ns/ttml}body element xml:id '
                         'omitted',
                message='timeContainer present but should be omitted',
                code=ValidationCode.dapt_timing_timecontainer
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}p element xml:id '
                         'p1',
                message='timeContainer seq prohibited',
                code=ValidationCode.dapt_timing_timecontainer
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 1.234s, end of doc is 2.0s',
                code=ValidationCode.ttml_document_timing
            ),
        ]
        self.assertFalse(valid)
        self.assertListEqual(vr, expected_validation_results)

    def test_daptTimingCheck_subs_overlap_segment(self):
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
        daptTimingCheck = daptTimingXmlCheck.daptTimingCheck(
            epoch=384,
            segment_dur=3.84,
            segment_relative_timing=False)
        vr = ValidationLogger()
        context = {}
        valid = daptTimingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='Timed content',
                message='Document content overlaps the segment '
                        'interval [384s..387.84s)',
                code=ValidationCode.dapt_timing_segment_overlap
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 380.0s, end of doc is 390.4s',
                code=ValidationCode.ttml_document_timing
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_daptTimingCheck_subs_wholly_within_segment(self):
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
        daptTimingCheck = daptTimingXmlCheck.daptTimingCheck(
            epoch=384,
            segment_dur=3.84,
            segment_relative_timing=False)
        vr = ValidationLogger()
        context = {}
        valid = daptTimingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='Timed content',
                message='Document content overlaps the segment '
                        'interval [384s..387.84s)',
                code=ValidationCode.dapt_timing_segment_overlap
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 384.5s, end of doc is 387.0s',
                code=ValidationCode.ttml_document_timing
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_daptTimingCheck_empty_doc_within_segment(self):
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
        daptTimingCheck = daptTimingXmlCheck.daptTimingCheck()
        vr = ValidationLogger()
        context = {}
        valid = daptTimingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=SKIP,
                location='{http://www.w3.org/ns/ttml}tt element',
                message='No body element found, skipping timing tests',
                code=ValidationCode.ttml_document_timing
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_daptTimingCheck_subs_end_before_segment(self):
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
        daptTimingCheck = daptTimingXmlCheck.daptTimingCheck(
            epoch=384,
            segment_dur=3.84,
            segment_relative_timing=False)
        vr = ValidationLogger()
        context = {}
        valid = daptTimingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='Timed content',
                message='Document content is timed outside the segment '
                        'interval [384s..387.84s)',
                code=ValidationCode.dapt_timing_segment_overlap
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 380.5s, end of doc is 384.0s',
                code=ValidationCode.ttml_document_timing
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_daptTimingCheck_subs_begin_after_segment(self):
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
        daptTimingCheck = daptTimingXmlCheck.daptTimingCheck(
            epoch=384,
            segment_dur=3.84,
            segment_relative_timing=False)
        vr = ValidationLogger()
        context = {}
        valid = daptTimingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='Timed content',
                message='Document content is timed outside the segment '
                        'interval [384s..387.84s)',
                code=ValidationCode.dapt_timing_segment_overlap
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 387.841s, end of doc is 390.0s',
                code=ValidationCode.ttml_document_timing
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_daptTimingCheck_timecode_delta_warn(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    xmlns:ebuttm="urn:ebu:tt:metadata"
    ttp:frameRate="25"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
<metadata>
<daptm:daptOriginTimecode>10:00:00:00</daptm:daptOriginTimecode>
<ebuttm:documentStartOfProgramme>10:00:01:00</ebuttm:documentStartOfProgramme>
</metadata>
</head>
<body><div>
<p begin="00:06:27.841" end="00:06:28.5" xml:id="p1"><span>after the segment 1</span></p>
<p begin="00:06:28.500" end="00:06:30" xml:id="p2"><span>after the segment 2</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        daptTimingCheck = daptTimingXmlCheck.daptTimingCheck()
        vr = ValidationLogger()
        context = {}
        valid = daptTimingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=WARN,
                location='Timecode-related metadata',
                message='Non-zero delta between daptOriginTimecode '
                        '10:00:00:00 and documentStartOfProgramme '
                        '10:00:01:00 suggests document times may need '
                        'to be offset by -1.000s',
                code=ValidationCode.dapt_timing_timecode_offset
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 387.841s, end of doc is 390.0s',
                code=ValidationCode.ttml_document_timing
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_daptTimingCheck_timecode_no_delta_dsop_offset_time(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    xmlns:ebuttm="urn:ebu:tt:metadata"
    ttp:frameRate="25"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
<metadata>
<daptm:daptOriginTimecode>10:00:00:00</daptm:daptOriginTimecode>
<ebuttm:documentStartOfProgramme>900000f</ebuttm:documentStartOfProgramme>
</metadata>
</head>
<body><div>
<p begin="00:06:27.841" end="00:06:28.5" xml:id="p1"><span>after the segment 1</span></p>
<p begin="00:06:28.500" end="00:06:30" xml:id="p2"><span>after the segment 2</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        daptTimingCheck = daptTimingXmlCheck.daptTimingCheck()
        vr = ValidationLogger()
        context = {}
        valid = daptTimingCheck.run(
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
                message='First text appears at 387.841s, end of doc is 390.0s',
                code=ValidationCode.ttml_document_timing
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_daptTimingCheck_bad_timecode_metadata_too_many(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    xmlns:ebuttm="urn:ebu:tt:metadata"
    ttp:frameRate="25"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
<metadata>
<daptm:daptOriginTimecode>10:00:00:00</daptm:daptOriginTimecode>
<daptm:daptOriginTimecode>10:00:04:00</daptm:daptOriginTimecode>
<ebuttm:documentStartOfProgramme>10:00:01:00</ebuttm:documentStartOfProgramme>
<ebuttm:documentStartOfProgramme>10:00:02:00</ebuttm:documentStartOfProgramme>
</metadata>
</head>
<body><div>
<p begin="00:06:27.841" end="00:06:28.5" xml:id="p1"><span>after the segment 1</span></p>
<p begin="00:06:28.500" end="00:06:30" xml:id="p2"><span>after the segment 2</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        daptTimingCheck = daptTimingXmlCheck.daptTimingCheck()
        vr = ValidationLogger()
        context = {}
        valid = daptTimingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='./{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}metadata/'
                         '{http://www.w3.org/ns/ttml/profile/dapt#metadata}'
                         'daptOriginTimecode',
                message='Expected max 1 daptOriginTimecode, found 2',
                code=ValidationCode.dapt_timing_origin_timecode
            ),
            ValidationResult(
                status=ERROR,
                location='./{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}metadata/'
                         '{urn:ebu:tt:metadata}documentStartOfProgramme',
                message='Expected max 1 documentStartOfProgramme, found 2',
                code=ValidationCode.dapt_timing_origin_timecode
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 387.841s, end of doc is 390.0s',
                code=ValidationCode.ttml_document_timing
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_daptTimingCheck_timecode_invalid_time_expressions(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    xmlns:ebuttm="urn:ebu:tt:metadata"
    ttp:frameRate="25"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
<metadata>
<daptm:daptOriginTimecode>900000f</daptm:daptOriginTimecode>
<ebuttm:documentStartOfProgramme>09:59:59:25</ebuttm:documentStartOfProgramme>
</metadata>
</head>
<body><div>
<p begin="00:06:27.841" end="00:06:28.5" xml:id="p1"><span>after the segment 1</span></p>
<p begin="00:06:28.500" end="00:06:30" xml:id="p2"><span>after the segment 2</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        daptTimingCheck = daptTimingXmlCheck.daptTimingCheck()
        vr = ValidationLogger()
        context = {}
        valid = daptTimingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='./{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}metadata/'
                         '{http://www.w3.org/ns/ttml/profile/dapt#metadata}'
                         'daptOriginTimecode',
                message='daptOriginTimecode value "900000f" is '
                        'not a valid format',
                code=ValidationCode.dapt_timing_origin_timecode
            ),
            ValidationResult(
                status=ERROR,
                location='./{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}metadata/'
                         '{urn:ebu:tt:metadata}documentStartOfProgramme',
                message='09:59:59:25 has illegal frame value '
                        'for frame rate 25',
                code=ValidationCode.ttml_timing_attribute_syntax
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 387.841s, end of doc is 390.0s',
                code=ValidationCode.ttml_document_timing
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_daptTimingCheck_origin_timecode_too_many_frames(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    xmlns:ebuttm="urn:ebu:tt:metadata"
    ttp:frameRate="25"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<head>
<metadata>
<daptm:daptOriginTimecode>09:59:59:25</daptm:daptOriginTimecode>
</metadata>
</head>
<body><div>
<p begin="00:06:27.841" end="00:06:28.5" xml:id="p1"><span>after the segment 1</span></p>
<p begin="00:06:28.500" end="00:06:30" xml:id="p2"><span>after the segment 2</span></p>
</div></body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        daptTimingCheck = daptTimingXmlCheck.daptTimingCheck()
        vr = ValidationLogger()
        context = {}
        valid = daptTimingCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='./{http://www.w3.org/ns/ttml}head/'
                         '{http://www.w3.org/ns/ttml}metadata/'
                         '{http://www.w3.org/ns/ttml/profile/dapt#metadata}'
                         'daptOriginTimecode',
                message='09:59:59:25 has illegal frame value '
                        'for frame rate 25',
                code=ValidationCode.ttml_timing_attribute_syntax
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at 387.841s, end of doc is 390.0s',
                code=ValidationCode.ttml_document_timing
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)
