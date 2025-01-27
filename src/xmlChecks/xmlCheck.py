from ..validationResult import ValidationResult, ERROR, GOOD
from xml.etree.ElementTree import Element
from ..ebuttdSchema import EBUTTDSchema
from xmlschema import XMLSchemaValidationError


class xmlCheck:

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: list[ValidationResult]) -> bool:
        raise NotImplementedError()


class xsdValidator(xmlCheck):

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: list[ValidationResult]) -> bool:
        valid = True
        try:
            EBUTTDSchema.validate(source=input)
        except XMLSchemaValidationError as e:
            valid = False
            validation_results.append(
                ValidationResult(
                    status=ERROR,
                    location=e.elem.tag,
                    message='Fails XSD validation: {}'.format(e.reason)
                ))
            context['is_ebuttd'] = False
        else:
            validation_results.append(
                ValidationResult(
                    status=GOOD,
                    location='',
                    message='XSD Validation passes'
                )
            )
            context['is_ebuttd'] = True
        return valid
