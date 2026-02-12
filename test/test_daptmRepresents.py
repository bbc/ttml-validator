# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

import unittest
import src.xmlChecks.daptmRepresentsCheck as daptmRepresentsCheck
import xml.etree.ElementTree as ElementTree
from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationResult import ValidationResult, \
    ERROR, GOOD


class testDaptmRepresentsCheck(unittest.TestCase):
    maxDiff = None

    def test_valid_content_descriptor(self):
        descriptors = [
            'audio',
            'audio.dialogue',
            'x-userdefined',
            'visual.x-userdefined',
            'visual.x-userdefined.subset',
        ]

        drc = daptmRepresentsCheck.daptmRepresentsCheck()

        for descriptor in descriptors:
            with self.subTest(descriptor=descriptor):
                self.assertTrue(
                    drc._is_valid_content_descriptor(descriptor=descriptor))

    def test_invalid_content_descriptor(self):
        descriptors = [
            '',
            '.',
            '.visual',
            'audio.'
            'userdefined',
            'audio.userdefined',
            'audio.dialogue.userdefined',
            'userdefined.audio',
        ]

        drc = daptmRepresentsCheck.daptmRepresentsCheck()

        for descriptor in descriptors:
            with self.subTest(descriptor=descriptor):
                self.assertFalse(
                    drc._is_valid_content_descriptor(descriptor=descriptor))

    def test_is_subtype_true(self):
        test_vals = [
            ('x', 'x'),
            ('x.y', 'x'),
            ('x.y.z', 'x'),
            ('x.y.z', 'x.y')
        ]

        for (subtype, parent) in test_vals:
            with self.subTest(subtype=subtype, parent=parent):
                self.assertTrue(
                    daptmRepresentsCheck._is_content_descriptor_subtype(
                        subtype=subtype, parent=parent)
                    )

    def test_is_subtype_false(self):
        test_vals = [
            ('x', 'y'),
            ('x.y', 'y'),
            ('x.y.z', 'x.z'),
            ('x.y.z', '.'),
            ('x', ''),
        ]

        for (subtype, parent) in test_vals:
            with self.subTest(subtype=subtype, parent=parent):
                self.assertFalse(
                    daptmRepresentsCheck._is_content_descriptor_subtype(
                        subtype=subtype, parent=parent)
                    )

    def test_scriptRepresents_good(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    daptm:scriptRepresents="audio visual.text x-userdefined.foo audio.x-userdefined">
</tt>"""
        input_elementtree = ElementTree.fromstring(input_xml)
        drc = daptmRepresentsCheck.daptmRepresentsCheck()
        vr = ValidationLogger()
        context = {}
        valid = drc.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ]
        self.assertListEqual(vr, expected_validation_results)

    def test_scriptRepresents_missing(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml">
</tt>"""
        input_elementtree = ElementTree.fromstring(input_xml)
        drc = daptmRepresentsCheck.daptmRepresentsCheck()
        vr = ValidationLogger()
        context = {}
        valid = drc.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}tt element',
                message='Required daptm:scriptRepresents attribute is missing',
                code=ValidationCode.dapt_metadata_scriptRepresents),
            ]
        self.assertListEqual(vr, expected_validation_results)

    def test_scriptRepresents_bad(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    daptm:scriptRepresents="audio.bad visual.text userdefined.audio . audio.x-userdefined">
</tt>"""
        input_elementtree = ElementTree.fromstring(input_xml)
        drc = daptmRepresentsCheck.daptmRepresentsCheck()
        vr = ValidationLogger()
        context = {}
        valid = drc.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}tt element '
                         'daptm:scriptRepresents attribute',
                message='Value audio.bad is not a valid content descriptor',
                code=ValidationCode.dapt_metadata_scriptRepresents),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}tt element '
                         'daptm:scriptRepresents attribute',
                message='Value userdefined.audio is not a valid content descriptor',
                code=ValidationCode.dapt_metadata_scriptRepresents),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}tt element '
                         'daptm:scriptRepresents attribute',
                message='Value . is not a valid content descriptor',
                code=ValidationCode.dapt_metadata_scriptRepresents),
            ]
        self.assertListEqual(vr, expected_validation_results)

    def test_computed_represents_good_inherited(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    daptm:scriptRepresents="audio"
    daptm:represents="audio.dialogue">
<body>
<div>
<p><span>dialogue</span></p>
</div>
</body>
</tt>"""
        input_elementtree = ElementTree.fromstring(input_xml)
        drc = daptmRepresentsCheck.daptmRepresentsCheck()
        vr = ValidationLogger()
        context = {}
        valid = drc.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ]
        self.assertListEqual(vr, expected_validation_results)

    def test_computed_represents_good_explicit(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    daptm:scriptRepresents="audio">
<body>
<div daptm:represents="audio.dialogue">
<p daptm:represents="audio.nonDialogueSounds"><span>dialogue</span></p>
</div>
</body>
</tt>"""
        input_elementtree = ElementTree.fromstring(input_xml)
        drc = daptmRepresentsCheck.daptmRepresentsCheck()
        vr = ValidationLogger()
        context = {}
        valid = drc.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertTrue(valid)
        expected_validation_results = [
            ]
        self.assertListEqual(vr, expected_validation_results)

    def test_computed_represents_bad_omitted(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    daptm:scriptRepresents="audio">
<body>
<div><!-- NB not a Script Event, no error for this -->
<div>
<p><span>dialogue</span></p>
</div>
</div>
</body>
</tt>"""
        input_elementtree = ElementTree.fromstring(input_xml)
        drc = daptmRepresentsCheck.daptmRepresentsCheck()
        vr = ValidationLogger()
        context = {}
        valid = drc.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div element '
                         'daptm:represents attribute',
                message='Computed value "" is not valid',
                code=ValidationCode.dapt_metadata_represents),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}p element '
                         'daptm:represents attribute',
                message='Computed value "" is not valid',
                code=ValidationCode.dapt_metadata_represents),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}span element '
                         'daptm:represents attribute',
                message='Computed value "" is not valid',
                code=ValidationCode.dapt_metadata_represents),
            ]
        self.assertListEqual(vr, expected_validation_results)
