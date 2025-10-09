import unittest
import src.xmlChecks.daptmDescTypeCheck as daptmDescTypeCheck
import xml.etree.ElementTree as ElementTree
from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationResult import ValidationResult, \
    ERROR, GOOD


class testDaptmDescTypeCheck(unittest.TestCase):
    maxDiff = None

    def test_valid_values(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    ttp:timeBase="media">
<body>
    <ttm:desc daptm:descType="x-extension"/>
    <div begin="10s" end="12s">
        <ttm:desc daptm:descType="scene">scene identifier</ttm:desc>
        <p>
            <ttm:desc daptm:descType="pronunciationNote">phoneme</ttm:desc>
            <span><ttm:desc>no descType</ttm:desc>some text</span>
        </p>
    </div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        dt_check = daptmDescTypeCheck.daptmDescTypeCheck()
        vr = ValidationLogger()
        context = {}
        valid = dt_check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='ttm:desc elements',
                message='3 well-formed descType attributes found',
                code=ValidationCode.dapt_metadata_desctype_validity
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_invalid_values(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    ttp:timeBase="media">
<body>
    <ttm:desc daptm:descType="invalid-extension"/>
    <div begin="10s" end="12s">
        <ttm:desc daptm:descType="scene">scene identifier</ttm:desc>
        <p>
            <ttm:desc daptm:descType="pronunciationNote">phoneme</ttm:desc>
            <span>some text</span>
        </p>
    </div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        dt_check = daptmDescTypeCheck.daptmDescTypeCheck()
        vr = ValidationLogger()
        context = {}
        valid = dt_check.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='ttm:desc element',
                message='invalid-extension is not a permitted value for '
                        'daptm:descType',
                code=ValidationCode.dapt_metadata_desctype_validity
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)
