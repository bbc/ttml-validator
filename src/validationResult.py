from dataclasses import dataclass

GOOD = 0
INFO = 1
WARN = 2
ERROR = 3

StatusStings = {
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

    def asString(self) -> str:
        return '{status}: {location} {message}'.format(
            status=StatusStings.get(self.status, 'UNKNOWN'),
            location=self.location,
            message=self.message,
        )
