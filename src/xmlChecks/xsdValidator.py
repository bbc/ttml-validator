from .xmlCheck import XmlCheck
from ..validationLogging.validationLogger import ValidationLogger
from ..validationLogging.validationCodes import ValidationCode
from xml.etree.ElementTree import Element
from xmlschema import XMLSchemaValidationError, XMLSchema


class xsdValidator(XmlCheck):

    def __init__(self,
                 xml_schema: XMLSchema,
                 schema_name: str) -> None:
        super().__init__()
        self._xmlSchema = xml_schema
        self._schemaName = schema_name

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        valid = True
        try:
            self._xmlSchema.validate(source=input)
        except XMLSchemaValidationError as e:
            valid = False
            validation_results.error(
                location=e.elem.tag,
                message='Fails {} XSD validation: {}'.format(
                    self._schemaName, e.reason),
                code=ValidationCode.xml_xsd
            )
        else:
            validation_results.good(
                location='Parsed document',
                message='{} XSD Validation passes'.format(self._schemaName),
                code=ValidationCode.xml_xsd
            )
        return valid
