from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from src.xmlUtils import get_unqualified_name, \
    xmlIdAttr, unqualifiedIdAttr, make_qname
from .xmlCheck import XmlCheck
from .ttmlUtils import ns_ttml


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


# Namespace prefixes will be mapped to document namespace later
IDREF_attr_to_applicable_elements = {
    'agent': ['ttm:agent'],
    'region': ['tt:region'],  # region must have a layout element ancestor
}

# Namespace prefixes will be mapped to document namespace later
IDREFS_attr_to_applicable_elements = {
    'style': [
        'tt:style'  # style must have a styling element ancestor
        ],
    'animate': [
        'tt:animate',  # must have an animation element ancestor
        'tt:set'  # must have an animation element ancestor
        ],
    'ttm:agent': [
        'ttm:agent'  # ttm:agent attribute != agent attribute!
        ],
}


def qualify(tag: str, tt_ns: str) -> str:
    if ':' not in tag:
        return tag

    colon_pos = tag.index(':')
    match tag[:colon_pos]:
        case 'tt':
            return make_qname(tt_ns, tag[colon_pos+1:])
        case 'ttm':
            return make_qname(tt_ns + '#metadata', tag[colon_pos+1:])

    return tag


def qualifyTags(attr_to_ell_map: dict[str, list[str]],
                tt_ns: str) -> dict[str, list[str]]:
    return {
        qualify(tag=k, tt_ns=tt_ns): [qualify(tag=vi, tt_ns=tt_ns) for vi in v]
        for k, v in attr_to_ell_map.items()
    }


class IDREFSelementApplicabilityCheck(XmlCheck):
    """
    Checks that IDREFS attributes dereference to an appropriate element.
    """

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        valid = True

        xmlIdToElementMap = context.get('xmlId_to_element_map')
        if xmlIdToElementMap is None:
            validation_results.skip(
                location=input.tag,
                message='Skipping IDREFS element applicability checks',
                code=ValidationCode.ttml_idref_element_applicability
            )
        else:
            # Qualify the attribute and element names
            tt_ns = \
                context.get('root_ns', ns_ttml)
            idref_map = qualifyTags(
                attr_to_ell_map=IDREF_attr_to_applicable_elements,
                tt_ns=tt_ns)
            idrefs_map = qualifyTags(
                attr_to_ell_map=IDREFS_attr_to_applicable_elements,
                tt_ns=tt_ns)
            all_idref_attrs = \
                set(idref_map.keys()).union(set(idrefs_map.keys()))

            # Iterate through element's descendants
            for el in input.iter():
                # For each element, check the attributes
                idrefs_attrs = sorted(set(el.keys()).intersection(all_idref_attrs))
                for attr in idrefs_attrs:
                    el_list = \
                        idref_map[attr] if attr in idref_map \
                        else idrefs_map[attr]
                    idrefs = el.get(attr, '').split()
                    if len(idrefs) == 0:
                        validation_results.error(
                            location='{} element {} attribute'
                                     .format(el.tag, attr),
                            message='Attribute must reference an element',
                            code=ValidationCode.ttml_idref_empty
                        )
                        valid = False
                    elif len(idrefs) > 1 and attr in idref_map:
                        validation_results.error(
                            location='{} element {} attribute'
                                     .format(el.tag, attr),
                            message='Attribute has {} references, 1 permitted'
                                    .format(len(idrefs)),
                            code=ValidationCode.ttml_idref_too_many
                        )
                        valid = False

                    for idref in idrefs:
                        ref_el_list = xmlIdToElementMap.get(idref)
                        ref_el = ref_el_list[0] \
                            if ref_el_list is not None and len(ref_el_list) == 1 \
                            else None

                        if ref_el is None or ref_el.tag not in el_list:
                            # Possible TODO: include element referenced,
                            # and acceptable list
                            validation_results.error(
                                location='{} element {} attribute reference {}'
                                         .format(el.tag, attr, idref),
                                message='Attribute references {} element, '
                                        'not in the list of acceptable elements'
                                        .format(ref_el.tag if ref_el is not None else 'no'),
                                code=ValidationCode
                                        .ttml_idref_element_applicability
                            )
                            valid = False

        return valid
