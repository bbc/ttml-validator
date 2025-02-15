import argparse
import sys
import logging
import re
import xml.etree.ElementTree as ElementTree
from .validationLogging.validationLogger import ValidationLogger
from .preParseChecks.preParseCheck import BadEncodingCheck, NullByteCheck, \
    ByteOrderMarkCheck
from .xmlChecks.xmlCheck import xsdValidator
from .xmlChecks.ttXmlCheck import duplicateXmlIdCheck, timeBaseCheck, \
    ttTagAndNamespaceCheck, activeAreaCheck, cellResolutionCheck, \
    unqualifiedIdAttributeCheck
from .xmlChecks.headXmlCheck import headCheck
from .xmlChecks.styleRefsCheck import styleRefsXmlCheck
from .xmlChecks.regionRefsCheck import regionRefsXmlCheck
from .xmlChecks.inlineStyleAttributeCheck import inlineStyleAttributesCheck
from .xmlChecks.bodyXmlCheck import bodyCheck
from .xmlChecks.timingXmlCheck import timingCheck
from pathlib import Path

logging.getLogger().setLevel(logging.INFO)


def log_results_summary(valid: bool):
    if valid:
        logging.info(
            'Document appears to be valid EBU-TT-D meeting BBC requirements '
            'and should play okay in the BBC\'s player.\n')
    else:
        logging.error(
            'Document is not valid EBU-TT-D meeting BBC '
            'requirements and is likely not to play properly if at all '
            'in the BBC\'s player.\n')


def get_epoch(args) -> float:
    epoch = 0.0
    if args.segment:
        filename = Path(args.ttml_in.name).name
        digits_re = re.compile(r'([0-9]+)[.]*')
        digits_match = digits_re.match(filename)
        if digits_match is not None:
            segment_number = float(digits_match.groups()[0])
            epoch = (segment_number - 1) * args.segdur
            logging.info(
                'Working epoch is {}s'.format(epoch)
            )
        else:
            logging.warning(
                'Could not gather epoch from input name {}'.format(filename))

    return epoch


def validate_ttml(args) -> int:
    logging.info('Validating {}'.format(args.ttml_in.name))
    logging.info('Writing results to {}'.format(args.results_out.name))

    epoch = get_epoch(args)
    dur = args.segdur if args.segment else None

    preParseChecks = [
        BadEncodingCheck(),  # check encoding before null bytes
        ByteOrderMarkCheck(),
        NullByteCheck(),
    ]

    xmlChecks = [
        xsdValidator(),
        unqualifiedIdAttributeCheck(),
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
        timingCheck(
            epoch=epoch,
            segment_dur=dur,
            segment_relative_timing=args.segment_relative_timing),
    ]

    validation_results = ValidationLogger()
    overall_valid = True

    in_bytes = args.ttml_in.read()
    for pre_parse_check in preParseChecks:
        current_check_name = ''
        try:
            current_check_name = type(pre_parse_check).__name__
            (check_valid, in_bytes) = \
                pre_parse_check.run(in_bytes, validation_results)
            overall_valid &= check_valid
        except Exception as e:
            overall_valid = False
            validation_results.error(
                location='While running ' + current_check_name,
                message='Exception raised: '+str(e)
            )

    try:
        in_xml_str = str(in_bytes, encoding='utf-8', errors='strict')
    except Exception as e:
        overall_valid = False
        validation_results.error(
                location='Unknown',
                message='Could not decode into UTF-8: '+str(e)
        )

    context = {}
    root = None
    try:
        root = ElementTree.fromstring(in_xml_str)
    except Exception as e:
        overall_valid = False
        validation_results.error(
            location='Document',
            message='Could not parse XML: '+str(e)
        )
    if root is not None:
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
                validation_results.error(
                    location='While running ' + current_check_name,
                    message='Exception raised: '+str(e)
                )

    if overall_valid:
        validation_results.good(
            location='Document',
            message='Document appears to be valid EBU-TT-D meeting '
                    'BBC requirements '
                    'and should play okay in the BBC\'s player.'
        )
    else:
        validation_results.error(
            location='Document',
            message='Document is not valid EBU-TT-D meeting BBC '
                    'requirements and is likely not to play properly'
                    ' if at all in the BBC\'s player.\n'
        )

    if args.collate_more_than and args.collate_more_than > 0:
        validation_results = validation_results.collateResults(
            more_than=args.collate_more_than)
    if args.csv:
        validation_results.write_csv(args.results_out)
    else:
        validation_results.write_plaintext(args.results_out)

    log_results_summary(overall_valid)

    return 0 if overall_valid else len(validation_results)


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
    parser.add_argument(
        '-segment',
        default=False,
        required=False,
        action='store_true',
        help='If set, get the segment number from the filename and '
             'use it to compute the expected begin time of the document.'
    )
    parser.add_argument(
        '-segdur',
        default='3.84',
        required=False,
        action='store',
        type=float,
        help='The segment duration in seconds (default 3.84).'
    )
    parser.add_argument(
        '-segment_relative_timing',
        default=False,
        required=False,
        action='store_true',
        help='If the content timings in the document are '
             'relative to the segment begin time (true) '
             'rather than the media timeline (false) (default false).'
    )
    parser.add_argument(
        '-collate_more_than',
        default='5',
        required=False,
        action='store',
        type=int,
        help='If more than zero, collates similar messages '
             'when there are more than the specified number.'
    )
    parser.set_defaults(func=validate_ttml)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    # execute only if run as a script
    sys.exit(main())
