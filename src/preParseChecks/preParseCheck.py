from typing import List
from ..validationResult import ValidationResult, ERROR, GOOD


class PreParseCheck:

    def run(
            self,
            input: bytes,
            validation_results: List[ValidationResult]) -> bytes:
        raise NotImplementedError()


class NullByteCheck(PreParseCheck):

    def run(
            self,
            input: bytes,
            validation_results: List[ValidationResult]) -> bytes:
        null_byte = b'\x00'
        if null_byte in input:
            validation_results.append(ValidationResult(
                status=ERROR,
                location='1st at byte {}'.format(input.index(null_byte)),
                message='Null byte(s) found in input'
            ))
            return input.replace(null_byte, b'')
        else:
            validation_results.append(ValidationResult(
                status=GOOD,
                location='',
                message='No null bytes found'
            ))
        return input


class BadEncodingCheck(PreParseCheck):

    def run(
            self,
            input: bytes,
            validation_results: List[ValidationResult]) -> bytes:

        # sirens for bad encoding - there's a chance of getting
        # false positives or false negatives. False positives
        # are very unlikely but if there are false negatives,
        # that's because different unicode code points are
        # wrongly encoded - add them to the list please!
        sirens = [
            b'\xc3\xa2\xc2\x80\xc2\x98',  # badly encoded U2018
            b'\xc3\xa2\xc2\x80\xc2\x99',  # badly encoded U2019
            b'\xc3\x83\xc2\xb8',  # badly encoded U00F8
        ]
        needs_reencoding = False
        for siren in sirens:
            needs_reencoding |= siren in input

        if needs_reencoding:
            validation_results.append(ValidationResult(
                status=ERROR,
                location='',
                message='Bad encoding found, re-encoding as UTF-8'
            ))
            output = str(input, encoding='utf-8').encode('latin-1')
            return output
        else:
            validation_results.append(ValidationResult(
                status=GOOD,
                location='',
                message='No bad encoding sirens found'
            ))

        return input
