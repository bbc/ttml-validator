from ..validationLogging.validationCodes import ValidationCode
from ..validationLogging.validationResult import ValidationResult, \
    ERROR, WARN
from ..validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from ..xmlUtils import make_qname
from .xmlCheck import XmlCheck
from ..registries.daptmDescTypeRegistry import descType_registry_entries, \
    descType_user_defined_value_prefix


class daptmDescTypeCheck(XmlCheck):
    """
    Checks values of daptm:descType attribute on ttm:descType elements
    """

    def __init__(self) -> None:
        super().__init__()

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        tt_ns = \
            context.get('root_ns', 'http://www.w3.org/ns/ttml')
        ttm_ns = tt_ns + '#metadata'
        desc_el_tag = make_qname(ttm_ns, 'desc')
        daptm_ns = 'http://www.w3.org/ns/ttml/profile/dapt#metadata'
        descType_attr_tag = make_qname(daptm_ns, 'descType')

        valid = True

        desc_els = input.findall(
            './/{}[@{}]'.format(desc_el_tag, descType_attr_tag))

        for desc_el in desc_els:
            descType_val = desc_el.get(descType_attr_tag)
            if descType_val \
               and not descType_val.startswith(
                   descType_user_defined_value_prefix) \
               and descType_val not in descType_registry_entries:
                valid = False
                validation_results.append(ValidationResult(
                    status=ERROR,
                    location='ttm:desc element',
                    message='{} is not a permitted value for daptm:descType'
                            .format(descType_val),
                    code=ValidationCode.dapt_metadata_desctype_validity
                ))

        if valid and len(desc_els) > 0:
            validation_results.good(
                location='ttm:desc elements',
                message='{} well-formed descType attributes found'
                        .format(len(desc_els)),
                code=ValidationCode.dapt_metadata_desctype_validity
            )
        elif valid:
            validation_results.info(
                location='ttm:desc elements',
                message='{} descType attributes found'
                        .format(len(desc_els)),
                code=ValidationCode.dapt_metadata_desctype_validity
            )

        return valid
