from ..validationLogging.validationLogger import ValidationLogger
from ..validationLogging.validationCodes import ValidationCode
import chardet
import codecs


class PreParseCheck:

    def run(
            self,
            input: bytes,
            validation_results: ValidationLogger) -> tuple[bool, bytes]:
        raise NotImplementedError()


class NullByteCheck(PreParseCheck):

    def run(
            self,
            input: bytes,
            validation_results: ValidationLogger) -> tuple[bool, bytes]:
        null_byte = b'\x00'
        if null_byte in input:
            validation_results.error(
                location='1st at byte {}'.format(input.index(null_byte)),
                message='Null byte(s) found in input',
                code=ValidationCode.preParse_nullBytes
            )
            return (False, input.replace(null_byte, b''))
        else:
            validation_results.good(
                location='Unparsed file',
                message='No null bytes found',
                code=ValidationCode.preParse_nullBytes
            )
        return (True, input)


class BadEncodingCheck(PreParseCheck):

    def run(
            self,
            input: bytes,
            validation_results: ValidationLogger) -> tuple[bool, bytes]:

        # sirens for bad encoding - there's a chance of getting
        # false positives or false negatives. False positives
        # are very unlikely but if there are false negatives,
        # that's because different unicode code points are
        # wrongly encoded - add them to the list please!
        utf8_as_latin1_sirens = [
            b'\xc3\xa2\xc2\x80\xc2\x98',  # badly encoded U2018 ‘
            b'\xc3\xa2\xc2\x80\xc2\x99',  # badly encoded U2019 ’
            b'\xc3\x83\xc2\xb8',  # badly encoded U00F8 ø
            b'\xc3\x83\xc2\xa0',  # badly encoded U00E0 à
            b'\xc3\x83\xc2\xb9',  # badly encoded U00F9 ù
            b'\xc3\x83\xc2\xa8',  # badly encoded U00E8 è
            b'\xc3\x83\xc2\xac',  # badly encoded U00EC ì
            b'\xc3\x83\xc2\xb2',  # badly encoded U00F2 ò
        ]
        utf8_as_latin1_found = False
        for utf8_as_latin1_siren in utf8_as_latin1_sirens:
            utf8_as_latin1_found |= utf8_as_latin1_siren in input

        if utf8_as_latin1_found:
            validation_results.error(
                location='Unparsed file',
                message='Bad latin-1 encoding found, re-encoding as UTF-8',
                code=ValidationCode.preParse_encoding
            )
            output = str(input, encoding='utf-8').encode('latin-1')
            return (False, output)

        # Detecting the encoding is not always accurate.
        # The chardet library tends to assume Windows-1252
        # as the most frequently used character encoding,
        # but will also report that UTF-8 is a possibility if it
        # hasn't ruled it out.
        # So we're going to assume UTF-8 if that's a possibility,
        # and only re-encode if it is definitely not UTF-8.
        # NB ASCII is a subset of UTF-8 so treat ascii as not needing
        # a re-encode.
        # Another approach would be to inspect the XML encoding
        # declaration and if it is UTF-8, and UTF-8 has not been ruled
        # out, use that, whereas if it is something else, that is also
        # in the "possibles" list, assume that is what it is,
        # and re-encode. However not doing that for now since we have
        # a separate check for the encoding in XMLStructureCheck
        detected = chardet.detect_all(input)
        detected_encodings = [d.get('encoding') for d in detected]
        if detected_encodings == [None]:
            validation_results.error(
                location='Unparsed file',
                message='No detectable encoding found, input may not be a '
                        'valid encoded byte sequence',
                code=ValidationCode.preParse_encoding
            )
            return (False, input)
        elif 'utf-8' not in detected_encodings \
             and 'ascii' not in detected_encodings:
            validation_results.error(
                location='Unparsed file',
                message='{} encoding found, with confidence {:.2f}, '
                        're-encoding as UTF-8'
                        .format(
                            detected[0]['encoding'],
                            detected[0]['confidence']),
                code=ValidationCode.preParse_encoding
            )
            # assume that if there is at least one encoding that is
            # not None then none of them will be None, and definitely
            # not the first one
            decoded = str(
                input,
                encoding=detected_encodings[0])  # type: ignore
            output = decoded.encode('utf-8')
            return (False, output)
        elif len(detected_encodings) > 1:
            validation_results.info(
                location='Unparsed file',
                message='Multiple possible encodings found including UTF-8 '
                        'or ASCII, assuming UTF-8 '
                        '(XML encoding declaration not checked)',
                code=ValidationCode.preParse_encoding
            )

        validation_results.good(
            location='Unparsed file',
            message='No bad encoding sirens found',
            code=ValidationCode.preParse_encoding
        )

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
            validation_results: ValidationLogger) -> tuple[bool, bytes]:

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
            validation_results.error(
                location='First {} bytes'.format(len(has_bom)),
                message='File has a prohibited Byte Order Mark (BOM): {} '
                        '- stripping UTF-8 BOM and continuing.'
                        .format(str(has_bom)),
                code=ValidationCode.preParse_byteOrderMark
            )
            output = input[len(has_bom):]
            return (False, output)
        elif has_bom:
            validation_results.error(
                location='First {} bytes'.format(len(has_bom)),
                message='File has a prohibited Byte Order Mark (BOM): {}'
                        ' - attempting to re-encode using codec {}'
                        .format(
                            str(has_bom),
                            self._boms_to_encodings[has_bom]),
                code=ValidationCode.preParse_byteOrderMark
            )
            output = codecs.encode(
                codecs.decode(
                    input[len(has_bom):], self._boms_to_encodings[has_bom]),
                'utf-8')
            return (False, output)
        elif has_weird_bom:
            validation_results.error(
                location='First {} bytes'.format(len(has_weird_bom)),
                message='File has a corrupt Byte Order Mark (BOM): {}'
                        ' - removing and hoping for the best.'
                        .format(
                            str(has_weird_bom)),
                code=ValidationCode.preParse_byteOrderMark_corrupt
                )
            output = input[len(has_weird_bom):]
            return (False, output)
        else:
            validation_results.good(
                location='Unparsed file',
                message='No Byte Order Mark (BOM) found',
                code=ValidationCode.preParse_byteOrderMark
            )

        return (True, input)
