from io import TextIOWrapper
from csv import writer as csvWriter
from typing import Self
from .validationResult import ValidationResult, \
    GOOD, INFO, WARN, ERROR


class ValidationLogger(list[ValidationResult]):
    def append(self, validation_result: ValidationResult):
        super().append(validation_result)

    def good(self, location: str, message: str):
        self.append(ValidationResult(
            status=GOOD,
            location=location,
            message=message
        ))

    def info(self, location: str, message: str):
        self.append(ValidationResult(
            status=INFO,
            location=location,
            message=message
        ))

    def warn(self, location: str, message: str):
        self.append(ValidationResult(
            status=WARN,
            location=location,
            message=message
        ))

    def error(self, location: str, message: str):
        self.append(ValidationResult(
            status=ERROR,
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
            seen_key = (vr.status, vr.message)
            seen_count = seen_messages.get(seen_key, 0)
            seen_count += 1
            seen_messages[seen_key] = seen_count

        messages_written = set()
        rv = ValidationLogger()
        for vr in self:
            seen_key = (vr.status, vr.message)
            seen_count = seen_messages.get(seen_key)
            if seen_count > more_than \
               and seen_key not in messages_written:
                rv.append(ValidationResult(
                    status=vr.status,
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
        headers = ['status', 'location', 'message']
        status_string_map = {
            GOOD: 'Pass',
            INFO: 'Info',
            WARN: 'Warn',
            ERROR: 'Fail',
        }
        stream.reconfigure(newline='')
        csv_writer = csvWriter(stream)
        csv_writer.writerow(headers)
        for result in self:
            csv_writer.writerow([
                status_string_map.get(result.status),
                result.location,
                result.message
            ])
