from ..validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from ..ebuttdSchema import EBUTTDSchema
from xmlschema import XMLSchemaValidationError


class xmlCheck:

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        raise NotImplementedError()


class xsdValidator(xmlCheck):

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        valid = True
        try:
            EBUTTDSchema.validate(source=input)
        except XMLSchemaValidationError as e:
            valid = False
            validation_results.error(
                location=e.elem.tag,
                message='Fails XSD validation: {}'.format(e.reason)
            )
            context['is_ebuttd'] = False
        else:
            validation_results.good(
                location='Parsed document',
                message='XSD Validation passes'
            )
            context['is_ebuttd'] = True
        return valid
