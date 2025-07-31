from ..validationLogging.validationCodes import ValidationCode
from ..validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from ..xmlUtils import get_unqualified_name, \
    xmlIdAttr, unqualifiedIdAttr
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


class unqualifiedIdAttributeCheck(XmlCheck):
    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:

        elements_with_xml_id = \
            set(input.findall('.//*[@{}]'.format(xmlIdAttr)))
        elements_with_unq_id = \
            set(input.findall('.//*[@{}]'.format(unqualifiedIdAttr)))
        num_elements_with_unq_id = len(elements_with_unq_id)
        num_elements_with_unq_id_and_xml_id = \
            len(elements_with_unq_id.intersection(elements_with_xml_id))
        num_elements_with_unq_id_and_no_xml_id = \
            num_elements_with_unq_id - num_elements_with_unq_id_and_xml_id

        if num_elements_with_unq_id_and_no_xml_id > 0 \
           or num_elements_with_unq_id > 0:
            validation_results.warn(
                location='Parsed document',
                message='{} elements have unqualified id attributes, '
                        'of which {} have no xml:id attribute. '
                        'Check if they should have xml:id attributes!'
                        .format(
                            num_elements_with_unq_id,
                            num_elements_with_unq_id_and_no_xml_id
                        ),
                code=ValidationCode.xml_id_unqualified
            )

        # Never fail on this
        return True


class duplicateXmlIdCheck(XmlCheck):

    @classmethod
    def _gatherXmlId(cls, e: Element, m: dict[str, list]):
        xmlId = e.get(xmlIdAttr)
        if xmlId:
            elist = m.get(xmlId, [])
            elist.append(e)
            m[xmlId] = elist

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        xmlIdToElementMap = {}

        for e in input.iter():
            duplicateXmlIdCheck._gatherXmlId(e=e, m=xmlIdToElementMap)

        valid = True
        for (xmlId, elist) in xmlIdToElementMap.items():
            if len(elist) > 1:
                valid = False
                validation_results.error(
                    location=', '.join(e.tag for e in elist),
                    message='Duplicate xml:id found with value ' + xmlId,
                    code=ValidationCode.xml_id_unique
                )
        if valid:
            validation_results.good(
                location='Parsed document',
                message='xml:id values are unique',
                code=ValidationCode.xml_id_unique
            )

        context['xmlId_to_element_map'] = xmlIdToElementMap

        return valid
