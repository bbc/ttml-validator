import unittest
import src.preParseChecks.preParseCheck as preParseCheck
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationResult import ValidationResult, \
    ERROR, GOOD
from src.validationLogging.validationCodes import ValidationCode


class testPreParseCheck(unittest.TestCase):

    maxDiff = None

    def test_no_direct_instantiation(self):
        not_impl_preparseCheck = preParseCheck.PreParseCheck()
        good_input = b'acdef'
        vr = ValidationLogger()

        with self.assertRaises(NotImplementedError):
            not_impl_preparseCheck.run(
                input=good_input,
                validation_results=vr)

    def testNullByteCheck(self):
        nullByteCheck = preParseCheck.NullByteCheck()
        good_input = b'abcdef'
        bad_input = b'abc\x00de\x00f'

        vr = ValidationLogger()
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
                message='No null bytes found',
                code=ValidationCode.preParse_nullBytes)
        ])

        vr = ValidationLogger()
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
            message='Null byte(s) found in input',
            code=ValidationCode.preParse_nullBytes
        )
        self.assertListEqual(vr, [expected_vr])

    def testBadEncodingCheck_good(self):
        badEncodingCheck = preParseCheck.BadEncodingCheck()
        # correctly UTF-8 encoded string
        good_input = b' boys don\xe2\x80\x99t'

        vr = ValidationLogger()
        valid, good_result = badEncodingCheck.run(
            input=good_input,
            validation_results=vr
        )

        # print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertEqual(good_result, good_input)
        self.assertTrue(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=GOOD,
                location='Unparsed file',
                message='No bad encoding sirens found',
                code=ValidationCode.preParse_encoding
            )
        ])

    def testBadEncodingCheck_bad_latin1(self):
        badEncodingCheck = preParseCheck.BadEncodingCheck()
        # two versions of the same string, one correctly UTF-8 encoded,
        # the other badly encoded, as we've seen in some files
        good_input = b' boys don\xe2\x80\x99t'
        bad_input = \
            b'\x20\x62\x6f\x79\x73\x20\x64\x6f\x6e\xc3\xa2\xc2\x80\xc2\x99\x74'

        vr = ValidationLogger()
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
                message='Bad latin-1 encoding found, re-encoding as UTF-8',
                code=ValidationCode.preParse_encoding)
        ])

    def testBadEncodingCheck_not_utf8(self):
        badEncodingCheck = preParseCheck.BadEncodingCheck()
        # two versions of the same string, one correctly UTF-8 encoded,
        # the other encoded in Windows-1252, as we've seen in some files
        good_input = b'This is Henry\xe2\x80\x99s monacle'
        bad_input = \
            b'This is Hen\x72\x79\x92\x73\x20\x6d\x6f\x6eacle'

        vr = ValidationLogger()
        valid, bad_result = badEncodingCheck.run(
            input=bad_input,
            validation_results=vr
        )

        # print('\n'+('\n'.join([v.asString() for v in vr])))
        self.assertEqual(bad_result, good_input)
        self.assertFalse(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=ERROR,
                location='Unparsed file',
                message='cp1250 encoding found, re-encoding as UTF-8',
                code=ValidationCode.preParse_encoding)
        ])

    @unittest.skip(
        "charset_normalizer considers empty byte sequences to be UTF-8, "
        "whereas libraries like chardet return an empty encoding list.")
    def testBadEncodingCheck_empty(self):
        badEncodingCheck = preParseCheck.BadEncodingCheck()

        empty_input = \
            b''

        vr = ValidationLogger()
        valid, empty_result = badEncodingCheck.run(
            input=empty_input,
            validation_results=vr
        )

        self.assertEqual(empty_result, empty_input)
        self.assertFalse(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=ERROR,
                location='Unparsed file',
                message='No detectable encoding found, input may not be a '
                        'valid encoded byte sequence',
                code=ValidationCode.preParse_encoding)
        ])

    def testBOMCheck(self):
        bomCheck = preParseCheck.ByteOrderMarkCheck()
        # two versions of the same string, one correctly UTF-8 encoded,
        # the other badly encoded, as we've seen in some files
        stimulus = 'some funky \u0800 text'
        good_result = stimulus.encode('utf-8')
        good_input = stimulus.encode('utf-8')
        utf8_bom_input = stimulus.encode('utf_8_sig')
        utf16_bom_input = stimulus.encode('utf-16')  # comes with a BOM!
        weird_input = \
            b'\xc3\xaf\xc2\xbb\xc2\xbf' \
            + good_input  # UTF-8 BOM encoded as UTF-8!

        # No BOM
        vr = ValidationLogger()
        valid, actual_result = bomCheck.run(
            input=good_input,
            validation_results=vr
        )

        self.assertEqual(good_result, actual_result)
        self.assertTrue(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=GOOD,
                location='Unparsed file',
                message='No Byte Order Mark (BOM) found',
                code=ValidationCode.preParse_byteOrderMark
            )
        ])

        # Valid UTF-8 BOM
        vr = ValidationLogger()
        valid, actual_result = bomCheck.run(
            input=utf8_bom_input,
            validation_results=vr
        )

        self.assertEqual(utf8_bom_input, actual_result)
        self.assertFalse(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=ERROR,
                location='First 3 bytes',
                message='File has a prohibited Byte Order Mark (BOM): '
                        'b\'\\xef\\xbb\\xbf\' - continuing.',
                code=ValidationCode.preParse_byteOrderMark)
        ])

        # Valid UTF-16 BOM
        vr = ValidationLogger()
        valid, actual_result = bomCheck.run(
            input=utf16_bom_input,
            validation_results=vr
        )

        self.assertEqual(utf16_bom_input, actual_result)
        self.assertFalse(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=ERROR,
                location='First 2 bytes',
                message='File has a prohibited Byte Order Mark (BOM): '
                        'b\'\\xff\\xfe\'',
                code=ValidationCode.preParse_byteOrderMark)
        ])

        # Weird BOM
        vr = ValidationLogger()
        valid, actual_result = bomCheck.run(
            input=weird_input,
            validation_results=vr
        )

        self.assertEqual(good_result, actual_result)
        self.assertFalse(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=ERROR,
                location='First 6 bytes',
                message='File has a corrupt Byte Order Mark (BOM): '
                        'b\'\\xc3\\xaf\\xc2\\xbb\\xc2\\xbf\' '
                        '- removing and hoping for the best.',
                code=ValidationCode.preParse_byteOrderMark_corrupt)
        ])
