from dataclasses import dataclass
from .validationCodes import ValidationCode

GOOD = 0
INFO = 1
WARN = 2
ERROR = 3
SKIP = 4

StatusStrings = {
    GOOD: 'Success',
    INFO: 'Information',
    WARN: 'Warning',
    ERROR: 'Error',
    SKIP: 'Skip',
}


@dataclass
class ValidationResult:
    status: int
    location: str
    message: str
    code: ValidationCode | None = None

    def _getCode(self) -> str:
        return self.code.name if self.code else ValidationCode.unclassified.name

    def asString(self) -> str:
        return '{status}: {code} {location} {message}'.format(
            status=StatusStrings.get(self.status, 'UNKNOWN'),
            code=self._getCode(),
            location=self.location,
            message=self.message,
        )

    def asDict(self) -> dict:
        return {
            'status': self.status,
            'location': self.location,
            'message': self.message,
            'code': self._getCode(),
        }
