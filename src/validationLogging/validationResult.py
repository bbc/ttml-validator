from dataclasses import dataclass
from .validationCodes import ValidationCode

GOOD = 0
INFO = 1
WARN = 2
ERROR = 3

StatusStrings = {
    GOOD: 'Success',
    INFO: 'Information',
    WARN: 'Warning',
    ERROR: 'Error',
}


@dataclass
class ValidationResult:
    status: int
    location: str
    message: str
    code: ValidationCode | None = None

    def asString(self) -> str:
        return '{status}: {code} {location} {message}'.format(
            status=StatusStrings.get(self.status, 'UNKNOWN'),
            code=self.code.name if self.code else ValidationCode.unclassified,
            location=self.location,
            message=self.message,
        )
