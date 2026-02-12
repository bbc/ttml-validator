# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

import unittest
import src.xmlChecks.ttmlRoleCheck as ttmlRoleCheck
import xml.etree.ElementTree as ElementTree
from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationResult import ValidationResult, \
    ERROR, GOOD, INFO


class testTtmRoleCheck(unittest.TestCase):
    maxDiff = None

    def test_valid_values(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:timeBase="media">
<body ttm:role="caption">
    <div begin="10s" end="12s" ttm:role="x-userdefined">
        <p ttm:role="dialog">
            <span ttm:role="expletive">some text</span>
        </p>
    </div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        input_body_el = \
            input_elementtree.find('./{http://www.w3.org/ns/ttml}body')
        self.assertIsNotNone(input_body_el)
        tr_check = ttmlRoleCheck.ttmlRoleTypeCheck()
        vr = ValidationLogger()
        context = {}
        valid = tr_check.run(
            input=input_body_el,  # ty:ignore[invalid-argument-type]
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}body element '
                         'and descendants',
                message='4 well-formed ttm:role attributes found',
                code=ValidationCode.ttml_metadata_role
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_invalid_values(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:timeBase="media">
<body ttm:role="invalid">
    <div begin="10s" end="12s" ttm:role="not conformant">
        <p ttm:role="nonsense">
            <span ttm:role="gibberish">some text</span>
        </p>
        <p ttm:role="caption">
            <span>valid role caption text</span>
        </p>
    </div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        input_body_el = \
            input_elementtree.find('./{http://www.w3.org/ns/ttml}body')
        self.assertIsNotNone(input_body_el)
        tr_check = ttmlRoleCheck.ttmlRoleTypeCheck()
        vr = ValidationLogger()
        context = {}
        valid = tr_check.run(
            input=input_body_el,  # ty:ignore[invalid-argument-type]
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}body element',
                message='"invalid" is not a permitted value for '
                        'ttm:role',
                code=ValidationCode.ttml_metadata_role
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div element',
                message='"not conformant" is not a permitted value for '
                        'ttm:role',
                code=ValidationCode.ttml_metadata_role
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}p element',
                message='"nonsense" is not a permitted value for '
                        'ttm:role',
                code=ValidationCode.ttml_metadata_role
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}span element',
                message='"gibberish" is not a permitted value for '
                        'ttm:role',
                code=ValidationCode.ttml_metadata_role
            ),
            ValidationResult(
                status=INFO,
                location='{http://www.w3.org/ns/ttml}body element '
                         'and descendants',
                message='1 well-formed ttm:role attribute found',
                code=ValidationCode.ttml_metadata_role
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)
