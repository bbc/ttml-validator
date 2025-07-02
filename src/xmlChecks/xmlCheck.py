from ..validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element


class XmlCheck:

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        raise NotImplementedError()
