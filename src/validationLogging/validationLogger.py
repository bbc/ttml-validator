# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

from io import TextIOWrapper
from csv import writer as csvWriter
import json
from typing import Self
from .validationCodes import ValidationCode
from .validationResult import ValidationResult, \
    GOOD, INFO, WARN, ERROR, SKIP


class ValidationLogger(list[ValidationResult]):
    def append(self, validation_result: ValidationResult):
        super().append(validation_result)

    def good(self,
             location: str,
             message: str,
             code: ValidationCode = ValidationCode.unclassified):
        self.append(ValidationResult(
            status=GOOD,
            code=code,
            location=location,
            message=message
        ))

    def info(self,
             location: str,
             message: str,
             code: ValidationCode = ValidationCode.unclassified):
        self.append(ValidationResult(
            status=INFO,
            code=code,
            location=location,
            message=message
        ))

    def warn(self,
             location: str,
             message: str,
             code: ValidationCode = ValidationCode.unclassified):
        self.append(ValidationResult(
            status=WARN,
            code=code,
            location=location,
            message=message
        ))

    def error(self,
              location: str,
              message: str,
              code: ValidationCode = ValidationCode.unclassified):
        self.append(ValidationResult(
            status=ERROR,
            code=code,
            location=location,
            message=message
        ))

    def skip(self,
              location: str,
              message: str,
              code: ValidationCode = ValidationCode.unclassified):
        self.append(ValidationResult(
            status=SKIP,
            code=code,
            location=location,
            message=message
        ))

    def collateResults(
            self,
            more_than: int) -> Self:
        # When we see the same status and message for more than
        # more_than messages, replace with a ValidationMessage
        # with the same status and message but set the location
        # to the number of messages found
        seen_messages = {}
        for vr in self:
            seen_key = (vr.status, vr.message, vr.code)
            seen_count = seen_messages.get(seen_key, 0)
            seen_count += 1
            seen_messages[seen_key] = seen_count

        messages_written = set()
        rv = ValidationLogger()
        for vr in self:
            seen_key = (vr.status, vr.message, vr.code)
            seen_count = seen_messages.get(seen_key)
            if seen_count > more_than \
               and seen_key not in messages_written:
                rv.append(ValidationResult(
                    status=vr.status,
                    code=vr.code,
                    location='{} locations'.format(seen_count),
                    message=vr.message
                ))
            elif seen_count <= more_than:
                rv.append(vr)
            messages_written.add(seen_key)

        return rv

    def write_plaintext(
            self,
            stream: TextIOWrapper,
            ):
        for result in self:
            stream.write(result.asString() + '\n')

    def write_csv(
            self,
            stream: TextIOWrapper,
            ):
        headers = ['status', 'code', 'location', 'message']
        status_string_map = {
            GOOD: 'Pass',
            INFO: 'Info',
            WARN: 'Warn',
            ERROR: 'Fail',
            SKIP: 'Skip',
        }
        stream.reconfigure(newline='')
        csv_writer = csvWriter(stream)
        csv_writer.writerow(headers)
        for result in self:
            csv_writer.writerow([
                status_string_map.get(result.status),
                result.code.name if result.code else '',
                result.location,
                result.message
            ])

    def write_json(
            self,
            stream: TextIOWrapper,
            ):
        stream.write(
            json.JSONEncoder().encode(
                [validation_result.asDict() for validation_result in self]
            )
        )
