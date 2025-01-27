from ..validationResult import ValidationResult, ERROR, GOOD, WARN, INFO
from xml.etree.ElementTree import Element
from ..xmlUtils import get_namespace, get_unqualified_name, make_qname, \
    xmlIdAttr
from .xmlCheck import xmlCheck
import re


class duplicateXmlIdCheck(xmlCheck):

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
            validation_results: list[ValidationResult]) -> bool:
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
            context: dict,
            validation_results: list[ValidationResult]) -> bool:
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
                 timeBase_whitelist: list[str] = ['media'],
                 timeBase_required: bool = False):
        super().__init__()
        self._timeBase_whitelist = timeBase_whitelist
        self._timeBase_required = timeBase_required

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: list[ValidationResult]) -> bool:
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
            context: dict,
            validation_results: list[ValidationResult]) -> bool:
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


class cellResolutionCheck(xmlCheck):
    cellResolution_re = re.compile(
        r'^(?P<horizontal>[\d]+)[\s]+'
        r'(?P<vertical>[\d]+)$')
    default_cellResolution = '32 15'  # defined by TTML spec

    def __init__(self,
                 cellResolution_required: bool = False):
        super().__init__()
        self._cellResolution_required = cellResolution_required

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: list[ValidationResult]) -> bool:
        ttp_ns = \
            context.get('root_ns', 'http://www.w3.org/ns/ttml') \
            + '#parameter'
        cellResolution_attr_key = make_qname(ttp_ns, 'cellResolution')
        valid = True

        if cellResolution_attr_key not in input.attrib:
            valid = not self._cellResolution_required
            validation_results.append(
                ValidationResult(
                    status=ERROR if self._cellResolution_required else WARN,
                    location='{} {} attribute'.format(
                        input.tag, cellResolution_attr_key),
                    message='{}cellResolution attribute absent'.format(
                        'Required ' if self._cellResolution_required else ''
                    )
                )
            )
            cellResolution_attr_val = self.default_cellResolution
            validation_results.append(
                ValidationResult(
                    status=INFO,
                    location='{} {} attribute'.format(
                        input.tag, cellResolution_attr_key),
                    message='using default cellResolution value {}'.format(
                        cellResolution_attr_val
                    )
                )
            )
        else:
            cellResolution_attr_val = input.get(cellResolution_attr_key)
            matches = self.cellResolution_re.match(cellResolution_attr_val)
            if matches:
                # check validity
                for g in ['horizontal', 'vertical']:
                    if int(matches.group(g)) == 0:
                        valid = False
                if not valid:
                    validation_results.append(
                        ValidationResult(
                            status=ERROR,
                            location='{} {} attribute'.format(
                                input.tag, cellResolution_attr_key),
                            message='cellResolution {} has '
                                    'at least one component == 0'.format(
                                cellResolution_attr_val)
                        )
                    )

            else:
                valid = False
                validation_results.append(
                    ValidationResult(
                        status=ERROR,
                        location='{} {} attribute'.format(
                            input.tag, cellResolution_attr_key),
                        message='cellResolution {} does not '
                                'match syntax requirements'.format(
                            cellResolution_attr_val)
                    )
                )

        if valid:
            validation_results.append(
                ValidationResult(
                    status=GOOD,
                    location='{} {} attribute'.format(
                        input.tag, cellResolution_attr_key),
                    message='cellResolution checked'
                )
            )
            context['cellResolution'] = cellResolution_attr_val
        else:
            context['cellResolution'] = self.default_cellResolution

        return valid
