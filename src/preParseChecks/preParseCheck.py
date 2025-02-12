from ..validationResult import ValidationResult, ERROR, GOOD
import codecs


class PreParseCheck:

    def run(
            self,
            input: bytes,
            validation_results: list[ValidationResult]) -> tuple[bool, bytes]:
        raise NotImplementedError()


class NullByteCheck(PreParseCheck):

    def run(
            self,
            input: bytes,
            validation_results: list[ValidationResult]) -> tuple[bool, bytes]:
        null_byte = b'\x00'
        if null_byte in input:
            validation_results.append(ValidationResult(
                status=ERROR,
                location='1st at byte {}'.format(input.index(null_byte)),
                message='Null byte(s) found in input'
            ))
            return (False, input.replace(null_byte, b''))
        else:
            validation_results.append(ValidationResult(
                status=GOOD,
                location='Unparsed file',
                message='No null bytes found'
            ))
        return (True, input)


class BadEncodingCheck(PreParseCheck):

    def run(
            self,
            input: bytes,
            validation_results: list[ValidationResult]) -> tuple[bool, bytes]:

        # sirens for bad encoding - there's a chance of getting
        # false positives or false negatives. False positives
        # are very unlikely but if there are false negatives,
        # that's because different unicode code points are
        # wrongly encoded - add them to the list please!
        utf8_as_latin1_sirens = [
            b'\xc3\xa2\xc2\x80\xc2\x98',  # badly encoded U2018
            b'\xc3\xa2\xc2\x80\xc2\x99',  # badly encoded U2019
            b'\xc3\x83\xc2\xb8',  # badly encoded U00F8
        ]
        needs_reencoding = False
        for utf8_as_latin1_siren in utf8_as_latin1_sirens:
            needs_reencoding |= utf8_as_latin1_siren in input

        if needs_reencoding:
            validation_results.append(ValidationResult(
                status=ERROR,
                location='Unparsed file',
                message='Bad latin-1 encoding found, re-encoding as UTF-8'
            ))
            output = str(input, encoding='utf-8').encode('latin-1')
            return (False, output)

        validation_results.append(ValidationResult(
            status=GOOD,
            location='Unparsed file',
            message='No bad encoding sirens found'
        ))

        return (True, input)


class ByteOrderMarkCheck(PreParseCheck):

    _boms_to_encodings = {
        codecs.BOM: 'utf_16',
        codecs.BOM_BE: 'utf_16_be',
        codecs.BOM_LE: 'utf_16_be',
        codecs.BOM_UTF8: 'utf_8',
        codecs.BOM_UTF16: 'utf_16',
        codecs.BOM_UTF16_BE: 'utf_16_be',
        codecs.BOM_UTF16_LE: 'utf_16_le',
        codecs.BOM_UTF32: 'utf_32',
        codecs.BOM_UTF32_BE: 'utf_32_be',
        codecs.BOM_UTF32_LE: 'utf_32_be',
    }

    _weird_boms = {
        b'\xc3\xaf\xc2\xbb\xc2\xbf',  # UTF-8 BOM encoded as UTF-8
    }

    def run(
            self,
            input: bytes,
            validation_results: list[ValidationResult]) -> tuple[bool, bytes]:

        has_bom = b''
        for bom in self._boms_to_encodings.keys():
            if input[0:len(bom)] == bom:
                has_bom = bom
                break

        has_weird_bom = b''
        for weird_bom in self._weird_boms:
            if input[0:len(weird_bom)] == weird_bom:
                has_weird_bom = weird_bom
                break

        if has_bom == codecs.BOM_UTF8:
            validation_results.append(ValidationResult(
                status=ERROR,
                location='First {} bytes'.format(len(has_bom)),
                message='File has a prohibited Byte Order Mark (BOM): {} '
                        '- stripping UTF-8 BOM and continuing.'
                        .format(str(has_bom))
            ))
            output = input[len(has_bom):]
            return (False, output)
        elif has_bom:
            validation_results.append(ValidationResult(
                status=ERROR,
                location='First {} bytes'.format(len(has_bom)),
                message='File has a prohibited Byte Order Mark (BOM): {}'
                        ' - attempting to re-encode using codec {}'
                        .format(
                            str(has_bom),
                            self._boms_to_encodings[has_bom])
            ))
            output = codecs.encode(
                codecs.decode(
                    input[len(has_bom):], self._boms_to_encodings[has_bom]),
                'utf-8')
            return (False, output)
        elif has_weird_bom:
            validation_results.append(ValidationResult(
                status=ERROR,
                location='First {} bytes'.format(len(has_weird_bom)),
                message='File has a corrupt Byte Order Mark (BOM): {}'
                        ' - removing and hoping for the best.'
                        .format(
                            str(has_weird_bom),
            )))
            output = input[len(has_weird_bom):]
            return (False, output)
        else:
            validation_results.append(ValidationResult(
                status=GOOD,
                location='Unparsed file',
                message='No Byte Order Mark (BOM) found'
            ))

        return (True, input)
