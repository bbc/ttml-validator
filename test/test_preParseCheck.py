import unittest
import src.preParseChecks.preParseCheck as preParseCheck
from src.validationResult import ValidationResult, ERROR, GOOD


class testPreParseCheck(unittest.TestCase):
    def testNullByteCheck(self):
        nullByteCheck = preParseCheck.NullByteCheck()
        good_input = b'abcdef'
        bad_input = b'abc\x00de\x00f'

        vr = []
        valid, good_result = nullByteCheck.run(
            input=good_input,
            validation_results=vr
        )

        self.assertEqual(good_input, good_result)
        self.assertTrue(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=GOOD,
                location='Unparsed file',
                message='No null bytes found')
        ])

        vr = []
        valid, bad_result = nullByteCheck.run(
            input=bad_input,
            validation_results=vr
        )
        # output should have null bytes removed
        self.assertEqual(good_input, bad_result)
        self.assertFalse(valid)
        expected_vr = ValidationResult(
            status=ERROR,
            location='1st at byte 3',
            message='Null byte(s) found in input'
        )
        self.assertListEqual(vr, [expected_vr])

    def testBadEncodingCheck(self):
        badEncodingCheck = preParseCheck.BadEncodingCheck()
        # two versions of the same string, one correctly UTF-8 encoded,
        # the other badly encoded, as we've seen in some files
        good_input = b' boys don\xe2\x80\x99t'
        bad_input = \
            b'\x20\x62\x6f\x79\x73\x20\x64\x6f\x6e\xc3\xa2\xc2\x80\xc2\x99\x74'

        vr = []
        valid, good_result = badEncodingCheck.run(
            input=good_input,
            validation_results=vr
        )

        self.assertEqual(good_result, good_input)
        self.assertTrue(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=GOOD,
                location='Unparsed file',
                message='No bad encoding sirens found'
            )
        ])

        vr = []
        valid, bad_result = badEncodingCheck.run(
            input=bad_input,
            validation_results=vr
        )

        self.assertEqual(bad_result, good_input)
        self.assertFalse(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=ERROR,
                location='Unparsed file',
                message='Bad encoding found, re-encoding as UTF-8')
        ])
