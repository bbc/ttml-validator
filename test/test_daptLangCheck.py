# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

import unittest
import src.xmlChecks.daptLangCheck as daptLangCheck
import xml.etree.ElementTree as ElementTree
from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationResult import ValidationResult, \
    ERROR, GOOD


class testDaptLangAudioNonMatchingCheck(unittest.TestCase):
    maxDiff = None

    def test_valid_audio_lang_unspecified(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    ttp:timeBase="media">
<body>
    <div begin="10s" end="12s">
        <p>
            <span>some text</span>
            <audio/>
        </p>
    </div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        check = daptLangCheck.daptLangAudioNonMatchingCheck()
        vr = ValidationLogger()
        context = {}
        valid = check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='audio elements',
                message='xml:lang checked',
                code=ValidationCode.dapt_lang_audio
            )
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_valid_audio_lang_specified(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    ttp:timeBase="media">
<body>
    <div begin="10s" end="12s">
        <p>
            <span>some text</span>
            <audio xml:lang="en-GB"/>
        </p>
    </div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        check = daptLangCheck.daptLangAudioNonMatchingCheck()
        vr = ValidationLogger()
        context = {}
        valid = check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='audio elements',
                message='xml:lang checked',
                code=ValidationCode.dapt_lang_audio
            )
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_invalid_audio_lang_empty(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    ttp:timeBase="media">
<body>
    <div begin="10s" end="12s">
        <p>
            <span>some text</span>
            <audio xml:lang=""/>
        </p>
    </div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        check = daptLangCheck.daptLangAudioNonMatchingCheck()
        vr = ValidationLogger()
        context = {}
        valid = check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='audio element xml:lang attribute',
                message='Computed value "" is not the same as parent '
                        'element computed value "en-GB"',
                code=ValidationCode.dapt_lang_audio
            )
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_invalid_audio_lang_non_empty(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    ttp:timeBase="media">
<body>
    <div begin="10s" end="12s">
        <p>
            <span>some text</span>
            <audio xml:lang="fr"/>
        </p>
    </div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        check = daptLangCheck.daptLangAudioNonMatchingCheck()
        vr = ValidationLogger()
        context = {}
        valid = check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='audio element xml:lang attribute',
                message='Computed value "fr" is not the same as parent '
                        'element computed value "en-GB"',
                code=ValidationCode.dapt_lang_audio
            )
        ]
        self.assertListEqual(vr, expected_validation_results)


class testNonEmptyLangRootCheck(unittest.TestCase):
    maxDiff = None

    def test_valid_root_lang(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    ttp:timeBase="media"/>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        check = daptLangCheck.nonEmptyLangRootCheck()
        vr = ValidationLogger()
        context = {}
        valid = check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt element',
                message='xml:lang present and not empty',
                code=ValidationCode.dapt_lang_root
            )
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_empty_root_lang(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang=""
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    ttp:timeBase="media"/>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        check = daptLangCheck.nonEmptyLangRootCheck()
        vr = ValidationLogger()
        context = {}
        valid = check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{{{}}}tt element'
                         .format('http://www.w3.org/ns/ttml'),
                message='Empty xml:lang attribute value prohibited',
                code=ValidationCode.dapt_lang_root
            )
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_missing_root_lang(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    ttp:timeBase="media"/>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        check = daptLangCheck.nonEmptyLangRootCheck()
        vr = ValidationLogger()
        context = {}
        valid = check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{{{}}}tt element'
                         .format('http://www.w3.org/ns/ttml'),
                message='Required xml:lang attribute is missing',
                code=ValidationCode.dapt_lang_root
            )
        ]
        self.assertListEqual(vr, expected_validation_results)
