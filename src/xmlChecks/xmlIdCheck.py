from ..validationLogging.validationCodes import ValidationCode
from ..validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from ..xmlUtils import get_unqualified_name, \
    xmlIdAttr
from .xmlCheck import XmlCheck


class requireXmlId(XmlCheck):
    """
    Checks that element has an xml:id attribute
    """

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:

        valid = True

        if xmlIdAttr not in input.keys():
            valid = False
            validation_results.error(
                location='{} xml:id omitted'.format(
                    get_unqualified_name(input.tag)),
                message='Element missing required xml:id attribute',
                code=ValidationCode.ebuttd_p_xml_id_constraint
            )

        return valid
