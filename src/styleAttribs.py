import re
from collections.abc import Callable
from dataclasses import dataclass, field
from xml.etree.ElementTree import Element
from .xmlUtils import make_qname, get_unqualified_name, get_namespace
from .validationLogging.validationCodes import ValidationCode
from .validationLogging.validationResult import ValidationResult, ERROR
from .validationLogging.validationLogger import ValidationLogger
# import logging
import types
from typing import TypeVar

styling_ns_suffix = '#styling'
ebutts_ns = 'urn:ebu:tt:style'
itts_ns = 'http://www.w3.org/ns/ttml/profile/imsc1#styling'

ebutt_distribution_color_type_regex = re.compile(
    r'^#(?P<r>[0-9a-fA-F]{2})'
    r'(?P<g>[0-9a-fA-F]{2})'
    r'(?P<b>[0-9a-fA-F]{2})'
    r'(?P<a>[0-9a-fA-F]{2})?$')

two_percent_vals_regex = re.compile(
    r'^(?P<x>[0]*((100(\.[0]+)?)|[\d]{1,2}(\.[\d]+)?))%'
    r'[\s]+'
    r'(?P<y>[0]*((100(\.[0]+)?)|[\d]{1,2}(\.[\d]+)?))%$')

percent_regex = \
    re.compile(r'^(?P<percent>[0-9]+(\.[0-9]+)?)%$')
basis_regex = \
    re.compile(r'^(?P<number>[0-9]+(\.[0-9]+)?)(?P<unit>[a-zA-Z%]*)$')

specified_type = TypeVar('specified', bound=str)
parent_type = TypeVar('parent', bound=str)
params_type = TypeVar('params', bound=dict[str, str])


@dataclass
class StyleAttribute:
    ns: str
    nsIsRelative: bool
    tag: str
    appliesTo: list[str]
    syntaxRegex: re.Pattern
    defaultValue: str
    computeValue: Callable[[specified_type, parent_type, params_type], str] = \
        field(hash=False, compare=False)

    def __post_init__(self):
        # Bind the computeValue method to self so it can access
        # object fields like syntaxRegex
        self.computeValue = types.MethodType(self.computeValue, self)

    def validateValue(self, value: str):
        syntax_match = self.syntaxRegex.match(value)
        return syntax_match is not None


def _computeUninheritedAttribute(
        self,
        specified: str,
        parent: str,
        params: dict[str, str]
) -> str:
    return specified if specified else self.defaultValue


def _computeSimpleInheritedAttribute(
        self,
        specified: str,
        parent: str,
        params: dict[str, str]
) -> str:
    rv = self.defaultValue if not specified else specified
    if parent and not specified:
        rv = parent
    # return parent if not specified else specified
    return rv


def _getPercentRelativeSize(
        specified: str,
        basis: str
) -> str:
    decoded_specified = percent_regex.match(specified)
    if decoded_specified:
        specified_float = float(decoded_specified.group('percent')) / 100
    else:
        raise ValueError(
            'Specified value {} is not a valid percentage value'
            .format(specified))

    decoded_basis = basis_regex.match(basis)
    if decoded_basis:
        basis_float = float(decoded_basis.group('number'))
        basis_unit = decoded_basis.group('unit')
    else:
        raise ValueError(
            'Basis value {} is not a valid number'
            .format(basis))

    return '{:.6f}{}'.format(specified_float * basis_float, basis_unit)


def _getCellHeight(params: dict[str, str]) -> str:
    unq_key = 'cellResolution'
    value = 100*1/15  # from default "32 15" value
    unit = 'rh'
    cellResolutionParams = {
        key: value for key, value in params.items()
        if get_unqualified_name(key) == unq_key}
    if len(cellResolutionParams) == 1:
        cellResolution = list(cellResolutionParams.values())[0]
        columns = cellResolution.split()[1]
        value = 100*1/int(columns)
    elif len(cellResolutionParams) > 1:
        raise ValueError('Too many {} parameters in {}'.format(
            unq_key,
            cellResolutionParams
        ))

    return '{:.6f}{}'.format(value, unit)


def _computeFontSize(
        self,  # Requires this to be used in the context of a StyleAttribute
        specified: str,
        parent: str,
        params: dict[str, str]
) -> str:
    # if it's a %, compute relative to parent, or cell height if no parent
    basis = parent if parent else _getCellHeight(params)

    if specified:
        specified_matches = self.syntaxRegex.match(specified)
        if specified_matches:
            specified_percent_val = specified_matches.group('percent')
            rv = _getPercentRelativeSize(specified_percent_val, basis) \
                if specified \
                else basis
        else:
            # if it's not a %, it's not conformant EBU-TT-D
            raise ValueError('{} is not a valid fontSize'.format(specified))
    else:
        rv = basis

    # store in the params so lineHeight can be computed
    params['fontSize'] = rv

    return rv


def _computeLineHeight(
        self,
        specified: str,
        parent: str,
        params: dict[str, str]
) -> str:
    rv = parent if parent else self.defaultValue

    # if specified, compute relative to the computed font size
    # (better have that in the params dict!)
    if specified and specified != 'normal':
        rv = _getPercentRelativeSize(specified, params['fontSize'])
    elif specified and specified == 'normal':
        rv = specified
    # otherwise inherit the computed value from the parent

    return rv


styleAttribs = \
    [
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='direction',
            appliesTo=['p', 'span'],
            syntaxRegex=re.compile(r'^(ltr)|(rtl)$'),
            defaultValue='ltr',
            computeValue=_computeSimpleInheritedAttribute
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='fontFamily',
            appliesTo=['span'],
            syntaxRegex=re.compile(
                r"""^(([-]?([_a-zA-Z]|[^\0-\237\\])([_a-zA-Z0-9\-]|[^\0-\237\\])*)([\s]+([-]?([_a-zA-Z]|[^\0-\237\\])([_a-zA-Z0-9\-]|[^\0-\237\\])*))*|(\"([^\"\\]|\\.)*\")|('([^'\\]|\\.)*'))([\s]*,[\s]*(([-]?([_a-zA-Z]|[^\0-\237\\])([_a-zA-Z0-9\-]|[^\0-\237\\])*)([\s]+([-]?([_a-zA-Z]|[^\0-\237\\])([_a-zA-Z0-9\-]|[^\0-\237\\])*))*|(\"([^\"\\]|\\.)*\")|('([^'\\]|\\.)*')))*$"""),
            defaultValue='default',
            computeValue=_computeSimpleInheritedAttribute
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='fontSize',
            appliesTo=['span'],
            syntaxRegex=re.compile(r'^(?P<percent>[\d]+(\.[\d]+)?%)$'),
            defaultValue='100%',
            computeValue=_computeFontSize
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='lineHeight',
            appliesTo=['p'],
            syntaxRegex=re.compile(r'^(normal)|([\d]+(\.[\d]+)?%)$'),
            defaultValue='normal',
            computeValue=_computeLineHeight
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='textAlign',
            appliesTo=['p'],
            syntaxRegex=re.compile(
                r'^(left)|(center)|(right)|(start)|(end)|(justify)$'),
            defaultValue='start',
            computeValue=_computeSimpleInheritedAttribute
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='color',
            appliesTo=['span'],
            syntaxRegex=ebutt_distribution_color_type_regex,
            defaultValue='#ffffffff',
            computeValue=_computeSimpleInheritedAttribute
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='backgroundColor',
            appliesTo=['region', 'body', 'div', 'p', 'span'],
            syntaxRegex=ebutt_distribution_color_type_regex,
            defaultValue='#00000000',
            computeValue=_computeUninheritedAttribute
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='fontStyle',
            appliesTo=['span'],
            syntaxRegex=re.compile(r'^(normal)|(italic)$'),
            defaultValue='normal',
            computeValue=_computeSimpleInheritedAttribute
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='fontWeight',
            appliesTo=['span'],
            syntaxRegex=re.compile(r'^(normal)|(bold)$'),
            defaultValue='normal',
            computeValue=_computeSimpleInheritedAttribute
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='textDecoration',
            appliesTo=['span'],
            syntaxRegex=re.compile(r'^(none)|(underline)$'),
            defaultValue='none',
            computeValue=_computeSimpleInheritedAttribute
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='unicodeBidi',
            appliesTo=['p', 'span'],
            syntaxRegex=re.compile(r'^(normal)|(embed)|(bidiOverride)$'),
            defaultValue='normal',
            computeValue=_computeSimpleInheritedAttribute
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='wrapOption',
            appliesTo=['span'],
            syntaxRegex=re.compile(r'^(wrap)|(noWrap)$'),
            defaultValue='wrap',
            computeValue=_computeSimpleInheritedAttribute
        ),
        StyleAttribute(
            ns=ebutts_ns,
            nsIsRelative=False,
            tag='multiRowAlign',
            appliesTo=['p'],
            syntaxRegex=re.compile(r'^(auto)|(start)|(center)|(end)$'),
            defaultValue='auto',
            computeValue=_computeSimpleInheritedAttribute
        ),
        StyleAttribute(
            ns=ebutts_ns,
            nsIsRelative=False,
            tag='linePadding',
            appliesTo=['p'],
            syntaxRegex=re.compile(r'^([\d]+(\.[\d]+)?)c$'),
            defaultValue='0c',
            computeValue=_computeSimpleInheritedAttribute
        ),
        StyleAttribute(
            ns=itts_ns,
            nsIsRelative=False,
            tag='fillLineGap',
            appliesTo=['p'],
            syntaxRegex=re.compile(r'^(false)|(true)$'),
            defaultValue='false',
            computeValue=_computeSimpleInheritedAttribute
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='origin',
            appliesTo=['region'],
            syntaxRegex=two_percent_vals_regex,
            defaultValue='0% 0%',
            computeValue=_computeUninheritedAttribute
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='extent',
            appliesTo=['region'],
            syntaxRegex=two_percent_vals_regex,
            defaultValue='100% 100%',
            computeValue=_computeUninheritedAttribute
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='displayAlign',
            appliesTo=['region'],  # Only on region in EBU-TT-D
            syntaxRegex=re.compile(
                r'^(before)|(center)|(after)$'),
            defaultValue='before',
            computeValue=_computeUninheritedAttribute
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='padding',
            appliesTo=['region'],  # Only on region in EBU-TT-D
            syntaxRegex=re.compile(
                r'^([\d]+(\.[\d]+)?%)([\s]+([\d]+(\.[\d]+)?%)){0,3}$'),
            defaultValue='0%',
            computeValue=_computeUninheritedAttribute
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='writingMode',
            appliesTo=['region'],
            syntaxRegex=re.compile(
                r'^(lrtb)|(rltb)|(tbrl)|(tblr)|(lr)|(rl)|(tb)$'),
            defaultValue='lrtb',
            computeValue=_computeUninheritedAttribute
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='showBackground',
            appliesTo=['region'],
            syntaxRegex=re.compile(
                r'^(always)|(whenActive)$'),
            defaultValue='always',
            computeValue=_computeUninheritedAttribute
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='overflow',
            appliesTo=['region'],
            syntaxRegex=re.compile(
                r'^(visible)|(hidden)$'),
            defaultValue='hidden',
            computeValue=_computeUninheritedAttribute
        ),
        StyleAttribute(
            ns='',
            nsIsRelative=False,
            tag='style',
            appliesTo=['style', 'region', 'body', 'div', 'p', 'span'],
            # The following regex does not properly match IDREFS but is an
            # approximation. It may falsely permit some non-conformant values
            syntaxRegex=re.compile(
                r'^([a-zA-Z_][\S]*([\t\f ]+([a-zA-Z_][\S]*))*)?$'),
            defaultValue='',
            computeValue=_computeUninheritedAttribute
        )
    ]

_elementsToApplicableStyleAttributes = {}
for styleAttrib in styleAttribs:
    for el_tag in styleAttrib.appliesTo:
        el_to_attrs = _elementsToApplicableStyleAttributes.get(
            el_tag, set()
        )
        el_to_attrs.add(styleAttrib.tag)
        _elementsToApplicableStyleAttributes[el_tag] = el_to_attrs
_allAttributeKeys = set(styleAttrib.tag for styleAttrib in styleAttribs)


def _makeTag(tt_ns: str, styleAttribute: StyleAttribute) -> str:
    tag = styleAttribute.tag
    ns = '{}{}'.format(
        tt_ns if styleAttribute.nsIsRelative else '',
        styleAttribute.ns)
    return make_qname(ns, tag)


def getStyleAttributeKeys(tt_ns: str, elements: list[str]) -> list[str]:
    el_set = set(elements)
    return [_makeTag(tt_ns=tt_ns, styleAttribute=sa)
            for sa in styleAttribs
            if not el_set.isdisjoint(sa.appliesTo)]


def getStyleAttributeDict(
        tt_ns: str, elements: list[str]) -> dict[str, StyleAttribute]:
    el_set = set(elements)
    return {_makeTag(tt_ns=tt_ns, styleAttribute=sa): sa
            for sa in styleAttribs
            if not el_set.isdisjoint(sa.appliesTo)}


def getAllStyleAttributeKeys(tt_ns: str) -> list[str]:
    return [_makeTag(tt_ns=tt_ns, styleAttribute=sa)
            for sa in styleAttribs]


def getAllStyleAttributeDict(tt_ns: str) -> dict[str, StyleAttribute]:
    return {_makeTag(tt_ns=tt_ns, styleAttribute=sa): sa
            for sa in styleAttribs}


def attributeIsApplicableToElement(attr_key: str, el_tag: str) -> bool:
    return \
        attr_key not in _allAttributeKeys \
        or attr_key in _elementsToApplicableStyleAttributes.get(el_tag, set())


def canonicaliseFontFamily(fontFamily: str) -> list[str]:
    if fontFamily is None:
        fontFamily = 'default'

    return [
        ff.strip() for ff in fontFamily.split(',')
    ]


def getMergedStyleSet(
        el: Element,
        id_to_styleattribs_map: dict[str, dict[str, str]],
) -> dict[str, str]:

    style_attr_val = el.get('style', '')
    ref_style_ids = style_attr_val.split()
    style_set = {}
    # Merge referential and chained referential styles
    for ref_style_id in ref_style_ids:
        attrib_dict = id_to_styleattribs_map.get(ref_style_id, {})
        for key, value in attrib_dict.items():
            if key != 'style':
                style_set[key] = value
    # Merge inline styles (even though there shouldn't be any)
    tt_ns = get_namespace(el.tag)
    style_attr_keys = getAllStyleAttributeKeys(tt_ns=tt_ns)
    for key in style_attr_keys:
        if key != 'style' and key in el.keys():
            style_set[key] = el.get(key)

    return style_set


def computeStyles(
        tt_ns: str,
        validation_results: ValidationLogger,
        el_sss: dict[str, str],
        el_css: dict[str, str],
        parent_css: dict[str, str],
        params: dict[str, str],
        error_significance: int = ERROR) -> bool:
    valid = True

    style_attrib_dict = getAllStyleAttributeDict(
        tt_ns=tt_ns)

    for style_key, style_attr in style_attrib_dict.items():
        try:
            specified = el_sss.get(style_key)
            if specified and not style_attr.validateValue(specified):
                raise ValueError('Value has invalid format')
            el_css[style_attr.tag] = style_attr.computeValue(
                specified=specified,
                parent=parent_css.get(style_attr.tag),
                params=params
            )
        except Exception as e:
            valid = False
            validation_results.append(ValidationResult(
                status=error_significance,
                location='{} styling attribute with value "{}"'.format(
                    style_key, el_sss.get(style_key)),
                message=str(e),
                code=ValidationCode.ttml_attribute_styling_attribute
            ))

    return valid
