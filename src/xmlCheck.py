from typing import Dict, List
from .validationResult import ValidationResult, ERROR, GOOD
from xml.etree.ElementTree import Element
from .ebuttdSchema import EBUTTDSchema
from xmlschema import XMLSchemaValidationError
from .xmlUtils import get_namespace, get_unqualified_name, make_qname

class xmlCheck:

    def run(
            self,
            input: Element,
            context: Dict,
            validation_results: List[ValidationResult]) -> bool:
        raise NotImplementedError()


class xsdValidator(xmlCheck):

    def run(
            self,
            input: Element,
            context: Dict,
            validation_results: List[ValidationResult]) -> bool:
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


class duplicateXmlIdCheck(xmlCheck):
    _xmlIdAttr = '{http://www.w3.org/XML/1998/namespace}id'

    @classmethod
    def _gatherXmlId(cls, e: Element, m: Dict[str, List]):
        xmlId = e.get(cls._xmlIdAttr)
        if xmlId:
            elist = m.get(xmlId, [])
            elist.append(e)
            m[xmlId] = elist

    def run(
            self,
            input: Element,
            context: Dict,
            validation_results: List[ValidationResult]) -> bool:
        xmlIdToElementMap = {}

        for e in input.iter():
            duplicateXmlIdCheck._gatherXmlId(e=e, m=xmlIdToElementMap)

        valid = True
        for (xmlId, elist) in xmlIdToElementMap.items():
            if len(elist) > 1:
                valid = False
                validation_results.append(ValidationResult(
                    status=ERROR,
                    location=', '.join(e.tag for e in elist),
                    message='Duplicate xml:id found with value ' + xmlId
                ))
        if valid:
            validation_results.append(ValidationResult(
                status=GOOD,
                location='',
                message='xml:id values are unique'
            ))

        context['xmlId_to_element_map'] = xmlIdToElementMap

        return valid


class ttTagAndNamespaceCheck(xmlCheck):
    def run(
            self,
            input: Element,
            context: Dict,
            validation_results: List[ValidationResult]) -> bool:
        ns = get_namespace(input.tag)
        unq_name = get_unqualified_name(input.tag)
        ttml_ns = 'http://www.w3.org/ns/ttml'
        ttml_root_el_name = 'tt'

        valid = True
        if ns != ttml_ns:
            valid = False
            validation_results.append(
                ValidationResult(
                    status=ERROR,
                    location=input.tag,
                    message='Element has unexpected namespace "{}"'.format(ns)
                )
            )
        if unq_name != ttml_root_el_name:
            valid = False
            validation_results.append(
                ValidationResult(
                    status=ERROR,
                    location=input.tag,
                    message='Element has unexpected tag <{}>'.format(unq_name)
                )
            )
        if valid:
            validation_results.append(
                ValidationResult(
                    status=GOOD,
                    location='Root element',
                    message='Document root has correct tag and namespace'
                )
            )

        context['root_ns'] = ns

        return valid


class timeBaseCheck(xmlCheck):
    default_timeBase = 'media'

    def __init__(self,
                 timeBase_whitelist: List[str] = ['media'],
                 timeBase_required: bool = False):
        super().__init__()
        self._timeBase_whitelist = timeBase_whitelist
        self._timeBase_required = timeBase_required

    def run(
            self,
            input: Element,
            context: Dict,
            validation_results: List[ValidationResult]) -> bool:
        ttp_ns = \
            context.get('root_ns', 'http://www.w3.org/ns/ttml') \
            + '#parameter'
        timeBase_attr_key = make_qname(ttp_ns, 'timeBase')
        valid = True

        if self._timeBase_required and timeBase_attr_key not in input.attrib:
            valid = False
            validation_results.append(
                ValidationResult(
                    status=ERROR,
                    location='{} {} attribute'.format(
                        input.tag, timeBase_attr_key),
                    message='Required timeBase attribute absent'
                )
            )

        timeBase_attr_val = \
            input.get(timeBase_attr_key, self.default_timeBase)
        if timeBase_attr_val not in self._timeBase_whitelist:
            valid = False
            validation_results.append(
                ValidationResult(
                    status=ERROR,
                    location='{} {} attribute'.format(
                        input.tag, timeBase_attr_key),
                    message='timeBase {} not in the allowed set {}'.format(
                        timeBase_attr_val, self._timeBase_whitelist)
                )
            )

        if valid:
            validation_results.append(
                ValidationResult(
                    status=GOOD,
                    location='{} {} attribute'.format(
                        input.tag, timeBase_attr_key),
                    message='timeBase checked'
                )
            )

        return valid
