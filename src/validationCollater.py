# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

"""
Read a set of CSV validation files,
count the number of Good, Info, Warn and Error
for each ValidationCode,
increment the number of each in an output CSV
file by 1 for every count >0.

For example:
3 files:
File 1 has:
* 1x Good xml_document_validity,
* 1x Good ebuttd_document_validity,
* 0x Good bbc_document_validity
* 1x Error bbc_document_validity

File 2 has:
* 1x Good xml_document_validity,
* 0x Good ebuttd_document_validity,
* 0x Good bbc_document_validity
* 1x Error bbc_document_validity

File 3 has:
* 1x Good xml_document_validity,
* 1x Good ebuttd_document_validity,
* 1x Good bbc_document_validity
* 0x Error bbc_document_validity

Result would be:

code,good_count,info_count,warn_count,error_count
xml_document_validity,3,0,0,0
ebuttd_document_validity,2,0,0,0
bbc_document_validity,1,0,0,2
"""
import argparse
import csv
import glob
import logging
from pathlib import Path
import sys
import traceback
from .validationLogging.validationCodes import ValidationCode

logging.getLogger().setLevel(logging.INFO)


out_headers = [
        'code',
        'good_count',
        'info_count',
        'warn_count',
        'error_count',
        'skip_count',
    ]

in_headers = [
    'status',
    'code',
    'location',
    'message',
    ]

status_string_map = dict(zip(
    [
        'Pass',
        'Info',
        'Warn',
        'Fail',
        'Skip',
    ],
    out_headers[1:]
    ))


def collate_validation(args) -> int:
    path = Path(args.validation_csv_path)
    val_filenames = glob.glob(str(path.expanduser()))
    logging.info(
        'Found {} matching files for {}'
        .format(len(val_filenames), args.validation_csv_path))
    if len(val_filenames) == 0:
        return 0

    collated_results = {
        vc.name: {h: 0 for h in out_headers[1:]}
        for vc in list(ValidationCode)}

    for val_filename in val_filenames:
        this_file_results = {
            vc.name: {h: 0 for h in out_headers[1:]}
            for vc in list(ValidationCode)}
        # print(this_file_results)
        logging.info('Processing {}'.format(val_filename))
        try:
            with open(val_filename, 'r', newline='') as val_file:
                val_file_reader = csv.DictReader(
                    f=val_file)

                for result in val_file_reader:
                    this_file_results[result['code']][
                        status_string_map[result['status']]
                        ] += 1

                for code, status_count in this_file_results.items():
                    for status, count in status_count.items():
                        if count > 0:
                            collated_results[code][status] += 1

        except Exception as e:
            logging.error(str(e), ''.join(traceback.format_exception(e)))

    out_csv = csv.writer(args.results_out)
    out_csv.writerow(out_headers)
    for code, status in collated_results.items():
        out_csv.writerow([code] + [count for count in status.values()])
    logging.info('Wrote results to {}'.format(args.results_out.name))

    return 0


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-validation_csv_path',
        type=str,
        required=True,
        help='Path where validation CSV files can be found. '
             'May include wildcards.',
        action='store')
    parser.add_argument(
        '-results_out',
        type=argparse.FileType('w'),
        default=sys.stdout,
        nargs='?',
        help='file to be written, containing the validation summary output',
        action='store')
    parser.set_defaults(func=collate_validation)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    # execute only if run as a script
    sys.exit(main())
