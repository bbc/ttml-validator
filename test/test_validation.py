# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationResult import ValidationResult, INFO
import src.validationLogging.validationSummariser as validationSummariser
from unittest import TestCase
import io


class testValidationLogging(TestCase):

    maxDiff = None

    def setUp(self):
        self.validationLogger = ValidationLogger()
        self.validationLogger.append(
            validation_result=ValidationResult(
                status=INFO,
                location='test location',
                message='test message',
            ))
        self.validationLogger.good(
            location='testloc1',
            message='simulated parse success',
            code=ValidationCode.xml_parse
        )
        self.validationLogger.warn(
            location='testloc1',
            message='simulated unqualified id warning',
            code=ValidationCode.xml_id_unqualified
        )
        self.validationLogger.error(
            location='testloc1',
            message='simulated xml id non-uniqueness',
            code=ValidationCode.xml_id_unique
        )
        self.validationLogger.error(
            location='testloc2',
            message='simulated xml id non-uniqueness',
            code=ValidationCode.xml_id_unique
        )
        self.validationLogger.error(
            location='testloc3',
            message='simulated xml id non-uniqueness',
            code=ValidationCode.xml_id_unique
        )
        self.validationLogger.warn(
            location='testloc1',
            message='simulated ttml document timing warning',
            code=ValidationCode.ttml_document_timing
        )
        self.validationLogger.skip(
            location='testloc4',
            message='simulated ebu-tt-d styling skip',
            code=ValidationCode.ebuttd_styling_element_constraint
        )
        self.validationLogger.error(
            location='testloc1',
            message='simulated BBC timing gaps error',
            code=ValidationCode.bbc_timing_gaps
        )
        return super().setUp()

    def test_writeCsv(self):
        tf = io.TextIOWrapper(
            buffer=io.BytesIO(), encoding='utf-8', newline='\n')
        self.validationLogger.write_csv(tf)
        tf.seek(0)
        result = tf.read()
        expected = """status,code,location,message\r
Info,,test location,test message\r
Pass,xml_parse,testloc1,simulated parse success\r
Warn,xml_id_unqualified,testloc1,simulated unqualified id warning\r
Fail,xml_id_unique,testloc1,simulated xml id non-uniqueness\r
Fail,xml_id_unique,testloc2,simulated xml id non-uniqueness\r
Fail,xml_id_unique,testloc3,simulated xml id non-uniqueness\r
Warn,ttml_document_timing,testloc1,simulated ttml document timing warning\r
Skip,ebuttd_styling_element_constraint,testloc4,simulated ebu-tt-d styling skip\r
Fail,bbc_timing_gaps,testloc1,simulated BBC timing gaps error\r
"""
        self.assertEqual(result, expected)

    def test_writeJson(self):
        tf = io.TextIOWrapper(
            buffer=io.BytesIO(), encoding='utf-8', newline='\n')
        self.validationLogger.write_json(tf)
        tf.seek(0)
        result = tf.read()
        expected = """[{"status": 1, "location": "test location", "message": "test message", "code": "unclassified"}, {"status": 0, "location": "testloc1", "message": "simulated parse success", "code": "xml_parse"}, {"status": 2, "location": "testloc1", "message": "simulated unqualified id warning", "code": "xml_id_unqualified"}, {"status": 3, "location": "testloc1", "message": "simulated xml id non-uniqueness", "code": "xml_id_unique"}, {"status": 3, "location": "testloc2", "message": "simulated xml id non-uniqueness", "code": "xml_id_unique"}, {"status": 3, "location": "testloc3", "message": "simulated xml id non-uniqueness", "code": "xml_id_unique"}, {"status": 2, "location": "testloc1", "message": "simulated ttml document timing warning", "code": "ttml_document_timing"}, {"status": 4, "location": "testloc4", "message": "simulated ebu-tt-d styling skip", "code": "ebuttd_styling_element_constraint"}, {"status": 3, "location": "testloc1", "message": "simulated BBC timing gaps error", "code": "bbc_timing_gaps"}]"""
        self.assertEqual(result, expected)

    def test_collateResults_and_write_plaintext(self):
        vl = self.validationLogger.collateResults(2)
        tf = io.TextIOWrapper(
            buffer=io.BytesIO(), encoding='utf-8', newline='\n')
        vl.write_plaintext(tf)
        tf.seek(0)
        result = tf.read()
        expected = """Information: unclassified test location test message
Success: xml_parse testloc1 simulated parse success
Warning: xml_id_unqualified testloc1 simulated unqualified id warning
Error: xml_id_unique 3 locations simulated xml id non-uniqueness
Warning: ttml_document_timing testloc1 simulated ttml document timing warning
Skip: ebuttd_styling_element_constraint testloc4 simulated ebu-tt-d styling skip
Error: bbc_timing_gaps testloc1 simulated BBC timing gaps error
"""
        self.assertEqual(result, expected)

    def test_validationSummariser(self):
        # tuples of checker, expected fails and expected warnings
        checks = [
            (validationSummariser.XmlPassChecker(), 3, 1, 0),
            (validationSummariser.TtmlPassChecker(), 0, 1, 0),
            (validationSummariser.EbuttdPassChecker(), 0, 0, 1),
            (validationSummariser.BbcPassChecker(), 1, 0, 0),
        ]

        for check in checks:
            with self.subTest(
                    checker=check[0],
                    fails=check[1],
                    warns=check[2],
                    skips=check[3],):
                result_fails, result_warns, result_skips = \
                    check[0].failuresAndWarningsAndSkips(self.validationLogger)
                self.assertEqual(check[1], result_fails)
                self.assertEqual(check[2], result_warns)
                self.assertEqual(check[3], result_skips)
