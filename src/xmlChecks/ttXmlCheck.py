from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationResult import ValidationResult, \
    ERROR, WARN
from src.validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from src.xmlUtils import get_namespace, get_unqualified_name, make_qname
from .xmlCheck import XmlCheck
from .ttmlUtils import ns_ttml
import re


class ttTagAndNamespaceCheck(XmlCheck):
    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        ns = get_namespace(input.tag)
        unq_name = get_unqualified_name(input.tag)
        ttml_root_el_name = 'tt'

        valid = True
        if ns != ns_ttml:
            valid = False
            validation_results.error(
                location=input.tag,
                message='Root element has unexpected namespace "{}"'
                .format(ns),
                code=ValidationCode.xml_tt_namespace
            )
        else:
            validation_results.good(
                location=input.tag,
                message='Root element has expected namespace "{}"'.format(ns),
                code=ValidationCode.xml_tt_namespace
            )
        if unq_name != ttml_root_el_name:
            valid = False
            validation_results.error(
                location=input.tag,
                message='Root element has unexpected tag <{}>'
                .format(unq_name),
                code=ValidationCode.xml_root_element
            )
        else:
            validation_results.good(
                location=input.tag,
                message='Root element has expected tag <{}>'.format(unq_name),
                code=ValidationCode.xml_root_element
            )

        context['root_ns'] = ns

        return valid


class timeBaseCheck(XmlCheck):
    default_timeBase = 'media'

    def __init__(self,
                 timeBase_acceptlist: list[str] = ['media'],
                 timeBase_required: bool = False):
        super().__init__()
        self._timeBase_acceptlist = timeBase_acceptlist
        self._timeBase_required = timeBase_required

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        ttp_ns = \
            context.get('root_ns', ns_ttml) \
            + '#parameter'
        timeBase_attr_key = make_qname(ttp_ns, 'timeBase')
        valid = True

        if self._timeBase_required and timeBase_attr_key not in input.attrib:
            valid = False
            validation_results.error(
                location='{} {} attribute'.format(
                    input.tag, timeBase_attr_key),
                message='Required timeBase attribute absent',
                code=ValidationCode.ebuttd_parameter_timeBase
            )

        timeBase_attr_val = \
            input.get(timeBase_attr_key, self.default_timeBase)
        if timeBase_attr_val not in self._timeBase_acceptlist:
            valid = False
            validation_results.error(
                location='{} {} attribute'.format(
                    input.tag, timeBase_attr_key),
                message='timeBase {} not in the allowed set {}'.format(
                    timeBase_attr_val, self._timeBase_acceptlist),
                code=ValidationCode.ebuttd_parameter_timeBase
            )

        if valid:
            validation_results.good(
                location='{} {} attribute'.format(
                    input.tag, timeBase_attr_key),
                message='timeBase checked',
                code=ValidationCode.ebuttd_parameter_timeBase
            )

        return valid


class activeAreaCheck(XmlCheck):
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
            validation_results: ValidationLogger) -> bool:
        ittp_ns = 'http://www.w3.org/ns/ttml/profile/imsc1#parameter'
        ittp_attr_key = make_qname(ittp_ns, 'activeArea')
        valid = True
        warn = False

        if ittp_attr_key not in input.attrib:
            valid = warn = not self._activeArea_required
            validation_results.append(
                ValidationResult(
                    status=ERROR if self._activeArea_required else WARN,
                    location='{} {} attribute'.format(
                        input.tag, ittp_attr_key),
                    message='{}activeArea attribute absent'.format(
                        'Required ' if self._activeArea_required else ''
                    ),
                    code=ValidationCode.imsc_parameter_activeArea
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
                    validation_results.error(
                        location='{} {} attribute'.format(
                            input.tag, ittp_attr_key),
                        message='activeArea {} has '
                                'at least one component >100%'.format(
                            ittp_attr_val),
                        code=ValidationCode.imsc_parameter_activeArea
                    )

            else:
                valid = False
                validation_results.error(
                    location='{} {} attribute'.format(
                        input.tag, ittp_attr_key),
                    message='activeArea {} does not '
                            'match syntax requirements'.format(
                        ittp_attr_val),
                    code=ValidationCode.imsc_parameter_activeArea
                )

        if valid and not warn:
            validation_results.good(
                location='{} {} attribute'.format(
                    input.tag, ittp_attr_key),
                message='activeArea checked',
                code=ValidationCode.imsc_parameter_activeArea
            )

        return valid


class cellResolutionCheck(XmlCheck):
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
            validation_results: ValidationLogger) -> bool:
        ttp_ns = \
            context.get('root_ns', ns_ttml) \
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
                        'Required ' if self._cellResolution_required else ''),
                    code=ValidationCode.ttml_parameter_cellResolution
                )
            )
            cellResolution_attr_val = self.default_cellResolution
            validation_results.info(
                location='{} {} attribute'.format(
                    input.tag, cellResolution_attr_key),
                message='using default cellResolution value {}'.format(
                    cellResolution_attr_val),
                code=ValidationCode.ttml_parameter_cellResolution
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
                    validation_results.error(
                        location='{} {} attribute'.format(
                            input.tag, cellResolution_attr_key),
                        message='cellResolution {} has '
                                'at least one component == 0'.format(
                            cellResolution_attr_val),
                        code=ValidationCode.ttml_parameter_cellResolution
                    )

            else:
                valid = False
                validation_results.error(
                    location='{} {} attribute'.format(
                        input.tag, cellResolution_attr_key),
                    message='cellResolution {} does not '
                            'match syntax requirements'.format(
                        cellResolution_attr_val),
                    code=ValidationCode.ttml_parameter_cellResolution
                )

        if valid:
            validation_results.good(
                location='{} {} attribute'.format(
                    input.tag, cellResolution_attr_key),
                message='cellResolution checked',
                code=ValidationCode.ttml_parameter_cellResolution
            )
            context['cellResolution'] = cellResolution_attr_val
        else:
            context['cellResolution'] = self.default_cellResolution

        return valid


class contentProfilesCheck(XmlCheck):

    def __init__(self,
                 contentProfiles_atleastonelist: list[str] = [],
                 contentProfiles_denylist: list[str] = [],
                 contentProfiles_required: bool = False):
        super().__init__()
        self._contentProfiles_atleastonelist = contentProfiles_atleastonelist
        self._contentProfiles_denylist = contentProfiles_denylist
        self._contentProfiles_required = contentProfiles_required

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        ttp_ns = \
            context.get('root_ns', ns_ttml) \
            + '#parameter'
        contentProfiles_attr_key = make_qname(ttp_ns, 'contentProfiles')
        valid = True

        if self._contentProfiles_required \
           and contentProfiles_attr_key not in input.attrib:
            valid = False
            validation_results.error(
                location='{} {} attribute'.format(
                    input.tag, contentProfiles_attr_key),
                message='Required contentProfiles attribute absent',
                code=ValidationCode.ttml_parameter_contentProfiles
            )

        contentProfiles_attr_val = \
            input.get(contentProfiles_attr_key, '')
        contentProfiles = contentProfiles_attr_val.split()
        at_least_one_found = False
        for contentProfile in contentProfiles:
            if contentProfile in self._contentProfiles_denylist:
                valid = False
                validation_results.error(
                    location='{} {} attribute'.format(
                        input.tag, contentProfiles_attr_key),
                    message='contentProfile {} present but '
                            'in the prohibited set {}'
                            .format(
                        contentProfile, self._contentProfiles_denylist),
                    code=ValidationCode.ttml_parameter_contentProfiles
                )
            if contentProfile in self._contentProfiles_atleastonelist:
                at_least_one_found = True

        if at_least_one_found is False \
           and len(self._contentProfiles_atleastonelist) > 0:
            valid = False
            validation_results.error(
                location='{} {} attribute'.format(
                    input.tag, contentProfiles_attr_key),
                message='At least one of the contentProfiles {} '
                        'must be present, all are missing from the '
                        'contentProfile attribute {}'.format(
                    self._contentProfiles_atleastonelist,
                    contentProfiles_attr_val),
                code=ValidationCode.ttml_parameter_contentProfiles
            )

        if valid:
            validation_results.good(
                location='{} {} attribute'.format(
                    input.tag, contentProfiles_attr_key),
                message='contentProfiles checked',
                code=ValidationCode.ttml_parameter_contentProfiles
            )

        return valid
