import argparse
import sys
import logging
# from csv import writer as csvWriter
import xml.etree.ElementTree as ElementTree
from .timeExpression import TimeExpressionHandler
from .validationResult import ValidationResult, GOOD, INFO, WARN, ERROR
from .preParseChecks.preParseCheck import BadEncodingCheck, NullByteCheck
from .xmlChecks.xmlCheck import xsdValidator
from .xmlChecks.ttXmlCheck import duplicateXmlIdCheck, timeBaseCheck, \
    ttTagAndNamespaceCheck, activeAreaCheck, cellResolutionCheck
from .xmlChecks.headXmlCheck import headCheck
from .xmlChecks.styleRefsCheck import styleRefsXmlCheck
from .xmlChecks.regionRefsCheck import regionRefsXmlCheck
from .xmlChecks.inlineStyleAttributeCheck import inlineStyleAttributesCheck
from .xmlChecks.bodyXmlCheck import bodyCheck
from .xmlChecks.timingXmlCheck import timingCheck
from io import TextIOBase

logging.getLogger().setLevel(logging.INFO)


preParseChecks = [
    BadEncodingCheck(),  # check encoding before null bytes
    NullByteCheck(),
]

xmlChecks = [
    xsdValidator(),
    duplicateXmlIdCheck(),
    ttTagAndNamespaceCheck(),
    timeBaseCheck(timeBase_whitelist=['media'], timeBase_required=True),
    activeAreaCheck(activeArea_required=False),
    cellResolutionCheck(cellResolution_required=False),
    headCheck(copyright_required=False),
    styleRefsXmlCheck(),
    inlineStyleAttributesCheck(),
    regionRefsXmlCheck(),
    bodyCheck(),
    timingCheck(),
]


def write_results(
        valid: bool,
        validation_results: list[ValidationResult],
        stream: TextIOBase,
        ):
    for result in validation_results:
        stream.write(result.asString() + '\n')
    if valid:
        stream.write(
            'Document appears to be valid EBU-TT-D meeting BBC requirements '
            'and should play okay in the BBC\'s player.\n')
    else:
        stream.write(
            'Errors found: document is not valid EBU-TT-D meeting BBC '
            'requirements and is likely not to play properly if at all '
            'in the BBC\'s player.\n')


def validate_ttml(args) -> int:
    logging.info('Validating {}'.format(args.ttml_in.name))
    logging.info('Writing results to {}'.format(args.results_out.name))
    validation_results = []
    overall_valid = True

    in_bytes = args.ttml_in.read()
    for pre_parse_check in preParseChecks:
        (check_valid, in_bytes) = pre_parse_check.run(in_bytes, validation_results)
        overall_valid &= check_valid

    try:
        in_xml_str = str(in_bytes, encoding='utf-8', errors='strict')
    except Exception as e:
        overall_valid = False
        validation_results.append(
            ValidationResult(
                status=ERROR,
                location='Unknown',
                message='Could not decode into UTF-8: '+str(e)
            )
        )

    context = {}
    root = ElementTree.fromstring(in_xml_str)
    for xml_check in xmlChecks:
        current_check_name = ''
        try:
            current_check_name = type(xml_check).__name__
            overall_valid &= xml_check.run(
                input=root,
                context=context,
                validation_results=validation_results
            )
        except Exception as e:
            overall_valid = False
            validation_results.append(
                ValidationResult(
                    status=ERROR,
                    location='While running '+ current_check_name,
                    message='Exception raised: '+str(e)
                )
            )

    write_results(overall_valid, validation_results, args.results_out)
    return len(validation_results)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-ttml_in',
        type=argparse.FileType('rb'),
        default=sys.stdin, nargs='?',
        help='Input TTML file to validate',
        action='store')
    parser.add_argument(
        '-results_out',
        type=argparse.FileType('w'),
        default=sys.stdout,
        nargs='?',
        help='file to be written, containing the validation results output',
        action='store')
    parser.add_argument(
        '-csv',
        default=False,
        required=False,
        action='store_true',
        help='If set, output in CSV format, with times')
    parser.set_defaults(func=validate_ttml)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    # execute only if run as a script
    main()
