from src.preParseChecks.preParseCheck import PreParseCheck
from src.xmlChecks.xmlCheck import XmlCheck
from src.validationLogging.validationLogger import ValidationLogger


class ConstraintSet():
    _preParseChecks = []
    _xmlChecks = []

    def preParseChecks(self) -> list[PreParseCheck]:
        return self._preParseChecks

    def xmlChecks(self) -> list[XmlCheck]:
        return self._xmlChecks

    @staticmethod
    def summarise(validation_results: ValidationLogger) -> tuple[int, int]:
        raise NotImplementedError
