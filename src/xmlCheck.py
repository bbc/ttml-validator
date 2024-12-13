from typing import Dict, List
from .validationResult import ValidationResult, ERROR, GOOD
from xml.etree import ElementTree
from .ebuttdSchema import EBUTTDSchema
from xmlschema import XMLSchemaValidationError


class xmlCheck:

    def run(
            self,
            input: ElementTree,
            context: Dict,
            validation_results: List[ValidationResult]) -> bool:
        raise NotImplementedError()


class xsdValidator(xmlCheck):

    def run(
            self,
            input: ElementTree,
            context: Dict,
            validation_results: List[ValidationResult]) -> bool:
        # valid = EBUTTDSchema.is_valid(input)
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
        else:
            validation_results.append(
                ValidationResult(
                    status=GOOD,
                    location='',
                    message='XSD Validation passes'
                )
            )
        return valid
