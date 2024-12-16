import argparse
import sys
import logging
# from csv import writer as csvWriter
from typing import Dict, List
import xml.etree.ElementTree as ElementTree
from .timeExpression import TimeExpressionHandler
from .validationResult import ValidationResult, GOOD, INFO, WARN, ERROR
from .preParseCheck import BadEncodingCheck, NullByteCheck
from .xmlCheck import xsdValidator, duplicateXmlIdCheck, ttTagAndNamespaceCheck, timeBaseCheck
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
    timeBaseCheck(timeBase_whitelist=['media'], timeBase_required=True)
]


def write_results(
        validation_results: List[ValidationResult],
        stream: TextIOBase,
        ):
    for result in validation_results:
        stream.write(result.asString())


def validate_ttml(args) -> int:
    logging.info('Validating {}'.format(args.ttml_in.name))
    logging.info('Writing results to {}'.format(args.results_out.name))
    validation_results = []

    in_bytes = args.ttml_in.read()
    for pre_parse_check in preParseChecks:
        in_bytes = pre_parse_check.run(in_bytes, validation_results)

    try:
        in_xml_str = str(in_bytes, encoding='utf-8', errors='strict')
    except Exception as e:
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
        xml_check.run(
            input=root,
            context=context,
            validation_results=validation_results
        )

    write_results(validation_results, args.results_out)
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
