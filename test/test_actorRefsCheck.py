import unittest
from src.xmlChecks.actorRefsCheck import actorRefsCheck
import xml.etree.ElementTree as ElementTree
from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationResult import ValidationResult, \
    ERROR, GOOD


class testActorRefsCheck(unittest.TestCase):
    maxDiff = None

    def test_okActorCheck(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata">
<head>
<metadata>
<ttm:agent type="character" xml:id="c1">
<ttm:name type="full">Character one</ttm:name>
<ttm:actor agent="p1"/>
</ttm:agent>
<ttm:agent type="person" xml:id="p1">
<ttm:name type="full">Person one</ttm:name>
</ttm:agent>
</metadata>
</head>
</tt>"""
        input_element = \
            ElementTree.fromstring(input_xml) \
            .find('./{http://www.w3.org/ns/ttml}head')
        self.assertIsNotNone(input_element)
        archeck = actorRefsCheck()
        vr = ValidationLogger()
        context = {}
        valid = archeck.run(
            input=input_element,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}head element',
                message='No ttm:actor elements found referencing'
                        ' ancestor ttm:agent',
                code=ValidationCode.ttml_metadata_actor_reference
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_badActorCheck(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata">
<head>
<metadata>
<ttm:agent type="character" xml:id="c1">
<ttm:name type="full">Character one</ttm:name>
<ttm:actor agent="c1"/>
</ttm:agent>
<ttm:agent type="person" xml:id="p1">
<ttm:name type="full">Person one</ttm:name>
</ttm:agent>
</metadata>
</head>
</tt>"""
        input_element = \
            ElementTree.fromstring(input_xml) \
            .find('./{http://www.w3.org/ns/ttml}head')
        self.assertIsNotNone(input_element)
        archeck = actorRefsCheck()
        vr = ValidationLogger()
        context = {}
        valid = archeck.run(
            input=input_element,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='ttm:agent element with xml:id=c1',
                message='ttm:actor element found with agent pointing '
                        'to ancestor ttm:agent element',
                code=ValidationCode.ttml_metadata_actor_reference
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)
