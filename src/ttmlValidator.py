# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

import argparse
import sys
import logging
import re
import io
import xml.etree.ElementTree as ElementTree
from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from src.constraintSets import constraintSet
from src.constraintSets.bbcConstraints import BbcSubtitleConstraintSet
from src.constraintSets.daptConstraints import DaptConstraintSet
from pathlib import Path

logging.getLogger().setLevel(logging.INFO)


def log_results_summary_bbc(valid: bool):
    if valid:
        logging.info(
            'Document appears to be valid EBU-TT-D meeting BBC requirements '
            'and should play okay in the BBC\'s player.')
    else:
        logging.error(
            'Document is not valid EBU-TT-D meeting BBC '
            'requirements.')


def log_results_summary_dapt(valid: bool):
    if valid:
        logging.info(
            'Document appears to be valid DAPT.')
    else:
        logging.error(
            'Document is not valid DAPT.')


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

    constraints = constraintSet.ConstraintSet()
    match args.flavour:
        case 'bbc':
            constraints = BbcSubtitleConstraintSet(
                epoch=epoch,
                segment_dur=dur,
                segment_relative_timing=args.segment_relative_timing
            )
        case 'dapt':
            constraints = DaptConstraintSet(
                epoch=epoch,
                segment_dur=dur,
                segment_relative_timing=args.segment_relative_timing
            )
        case other_flavour:
            logging.exception(
                'Flavour {} not recognised.'.format(other_flavour))

    preParseChecks = constraints.preParseChecks()
    xmlChecks = constraints.xmlChecks()

    validation_results = ValidationLogger()
    overall_valid = True

    # If stdin is used then we get a TextIOBase, but we want to read bytes
    buffer = args.ttml_in \
        if isinstance(args.ttml_in, io.BufferedIOBase) \
        else args.ttml_in.buffer
    in_bytes = buffer.read()
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
                message='Exception raised: ' + str(e),
                code=ValidationCode.validator_internal_exception
            )

    try:
        in_xml_str = str(in_bytes, encoding='utf-8', errors='strict')
    except Exception as e:
        overall_valid = False
        validation_results.error(
            location='Unknown',
            message='Could not decode into UTF-8: ' + str(e),
            code=ValidationCode.preParse_encoding
        )
        in_xml_str = ''

    context = {
        "args": {
            "vertical": True if args.vertical else False,
        }
    }
    root = None
    try:
        root = ElementTree.fromstring(in_xml_str)
    except Exception as e:
        overall_valid = False
        validation_results.error(
            location='Document',
            message='Could not parse XML: ' + str(e),
            code=ValidationCode.xml_parse
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
                    message='Exception raised: ' + str(e),
                    code=ValidationCode.validator_internal_exception
                )

    totalFails, totalSkips = constraints.summarise(
        validation_results)
    if overall_valid != (totalFails == 0 and totalSkips == 0):
        validation_results.error(
            location='Document validity summaries',
            message='Overall validity {} mismatch'.format(overall_valid),
            code=ValidationCode.validator_internal_exception
        )

    if args.collate_more_than and args.collate_more_than > 0:
        validation_results = validation_results.collateResults(
            more_than=args.collate_more_than)
    if args.csv:
        validation_results.write_csv(args.results_out)
    elif args.json:
        validation_results.write_json(args.results_out)
    else:
        validation_results.write_plaintext(args.results_out)
    args.results_out.flush()

    match args.flavour:
        case 'bbc':
            log_results_summary_bbc(overall_valid)
        case 'dapt':
            log_results_summary_dapt(overall_valid)

    return 0 if overall_valid else totalFails


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
        help='If set, output in CSV format')
    parser.add_argument(
        '-json',
        default=False,
        required=False,
        action='store_true',
        help='If set, output in JSON format')
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
        '-vertical',
        default=False,
        required=False,
        action='store_true',
        help='Set if the subtitle file is intended for presentation '
             'against a vertical/portrait (9:16 aspect ratio) video.'
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
    parser.add_argument(
        '-flavour',
        default='bbc',
        required=False,
        action='store',
        type=str,
        help='bbc (subtitles) or dapt'
    )
    parser.set_defaults(func=validate_ttml)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    # execute only if run as a script
    sys.exit(main())
