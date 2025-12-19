from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationResult import ValidationResult, \
    ERROR
from src.validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from src.xmlUtils import make_qname
from .xmlCheck import XmlCheck
from .ttmlUtils import ns_ttml
from src.registries.ttmRoleRegistry import role_registry_entries, \
    role_user_defined_value_prefix


class ttmlRoleTypeCheck(XmlCheck):
    """
    Checks values of ttm:role attribute
    """

    def __init__(self) -> None:
        super().__init__()

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        tt_ns: str = \
            context.get('root_ns', ns_ttml)
        ttm_ns: str = tt_ns + '#metadata'
        role_attr_tag: str = make_qname(ttm_ns, 'role')

        valid = True

        role_els: list[Element[str]] = input.findall(
            './/*[@{}]'.format(role_attr_tag))

        for role_el in role_els:
            role_val = role_el.get(role_attr_tag)
            if role_val \
               and not role_val.startswith(
                    role_user_defined_value_prefix) \
               and role_val not in role_registry_entries:
                valid = False
                validation_results.append(ValidationResult(
                    status=ERROR,
                    location='{} element'
                             .format(role_el.tag),
                    message='"{}" is not a permitted value for ttm:role'
                            .format(role_val),
                    code=ValidationCode.ttml_metadata_role
                ))

        if valid and len(role_els) > 0:
            validation_results.good(
                location='{} element and descendants'
                         .format(input.tag),
                message='{} well-formed ttm:role attributes found'
                        .format(len(role_els)),
                code=ValidationCode.ttml_metadata_role
            )
        elif valid:
            validation_results.info(
                location='{} element and descendants'
                         .format(input.tag),
                message='{} ttm:role attributes found'
                        .format(len(role_els)),
                code=ValidationCode.ttml_metadata_role
            )

        return valid
