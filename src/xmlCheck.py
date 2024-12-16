from typing import Dict, List
from .validationResult import ValidationResult, ERROR, GOOD, WARN
from xml.etree.ElementTree import Element
from .ebuttdSchema import EBUTTDSchema
from xmlschema import XMLSchemaValidationError
from .xmlUtils import get_namespace, get_unqualified_name, make_qname
import re

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


class activeAreaCheck(xmlCheck):
    activeArea_re = re.compile(
        r'^(?P<leftOffset>[\d]+(\.[\d]+)?)%[\s]+'
        r'(?P<topOffset>[\d]+(\.[\d]+)?)%[\s]+'
        r'(?P<width>[\d]+(\.[\d]+)?)%[\s]+'
        r'(?P<height>[\d]+(\.[\d]+)?)%$')

    def __init__(self,
                 activeArea_required: bool = False):
        super().__init__()
        self._activeArea_required = activeArea_required

    def run(
            self,
            input: Element,
            context: Dict,
            validation_results: List[ValidationResult]) -> bool:
        ittp_ns = 'http://www.w3.org/ns/ttml/profile/imsc1#parameter'
        ittp_attr_key = make_qname(ittp_ns, 'activeArea')
        valid = True

        if ittp_attr_key not in input.attrib:
            valid = not self._activeArea_required
            validation_results.append(
                ValidationResult(
                    status=ERROR if self._activeArea_required else WARN,
                    location='{} {} attribute'.format(
                        input.tag, ittp_attr_key),
                    message='{}activeArea attribute absent'.format(
                        'Required ' if self._activeArea_required else ''
                    )
                )
            )
        else:
            ittp_attr_val = input.get(ittp_attr_key)
            matches = self.activeArea_re.match(ittp_attr_val)
            if matches:
                # check validity
                for g in ['leftOffset', 'topOffset', 'width', 'height']:
                    if float(matches.group(g)) > 100:
                        valid = False
                if not valid:
                    validation_results.append(
                        ValidationResult(
                            status=ERROR,
                            location='{} {} attribute'.format(
                                input.tag, ittp_attr_key),
                            message='activeArea {} has '
                                    'at least one component >100%'.format(
                                ittp_attr_val)
                        )
                    )

            else:
                valid = False
                validation_results.append(
                    ValidationResult(
                        status=ERROR,
                        location='{} {} attribute'.format(
                            input.tag, ittp_attr_key),
                        message='activeArea {} does not '
                                'match syntax requirements'.format(
                            ittp_attr_val)
                    )
                )

        if valid:
            validation_results.append(
                ValidationResult(
                    status=GOOD,
                    location='{} {} attribute'.format(
                        input.tag, ittp_attr_key),
                    message='activeArea checked'
                )
            )

        return valid
