import re
from dataclasses import dataclass
from typing import Dict, List
from .xmlUtils import make_qname

styling_ns_suffix = '#styling'
ebutts_ns = 'urn:ebu:tt:style'
itts_ns = 'http://www.w3.org/ns/ttml/profile/imsc1#styling'

ebutt_distribution_color_type_regex = \
    r'^#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})?$'


@dataclass
class StyleAttribute:
    ns: str
    nsIsRelative: bool
    tag: str
    appliesTo: List[str]
    syntaxRegex: re.Pattern
    defaultValue: str


styleAttribs = \
    [
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='direction',
            appliesTo=['p', 'span'],
            syntaxRegex=re.compile(r'^(ltr)|(rtl)$'),
            defaultValue='ltr'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='fontFamily',
            appliesTo=['span'],
            syntaxRegex=re.compile(r'.*'),  # TODO
            defaultValue='default'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='fontSize',
            appliesTo=['span'],
            syntaxRegex=re.compile(r'^([\d]+(\.[\d]+)?%)$'),
            defaultValue='100%'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='lineHeight',
            appliesTo=['p'],
            syntaxRegex=re.compile(r'^(normal)|([\d]+(\.[\d]+)?%)$'),
            defaultValue='100%'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='textAlign',
            appliesTo=['p'],
            syntaxRegex=re.compile(
                r'^(left)|(center)|(right)|(start)|(end)|(justify)$'),
            defaultValue='start'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='color',
            appliesTo=['span'],
            syntaxRegex=re.compile(ebutt_distribution_color_type_regex),
            defaultValue='#ffffffff'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='backgroundColor',
            appliesTo=['region', 'body', 'div', 'p', 'span'],
            syntaxRegex=re.compile(ebutt_distribution_color_type_regex),
            defaultValue='#ffffffff'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='fontStyle',
            appliesTo=['span'],
            syntaxRegex=re.compile(r'^(normal)|(italic)$'),
            defaultValue='normal'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='fontWeight',
            appliesTo=['span'],
            syntaxRegex=re.compile(r'^(normal)|(bold)$'),
            defaultValue='normal'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='textDecoration',
            appliesTo=['span'],
            syntaxRegex=re.compile(r'^(none)|(underline)$'),
            defaultValue='none'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='unicodeBidi',
            appliesTo=['p', 'span'],
            syntaxRegex=re.compile(r'^(normal)|(embed)|(bidiOverride)$'),
            defaultValue='normal'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='wrapOption',
            appliesTo=['span'],
            syntaxRegex=re.compile(r'^(wrap)|(noWrap)$'),
            defaultValue='wrap'
        ),
        StyleAttribute(
            ns=ebutts_ns,
            nsIsRelative=False,
            tag='multiRowAlign',
            appliesTo=['p'],
            syntaxRegex=re.compile(r'^(auto)|(start)|(center)|(end)$'),
            defaultValue='auto'
        ),
        StyleAttribute(
            ns=ebutts_ns,
            nsIsRelative=False,
            tag='linePadding',
            appliesTo=['p'],
            syntaxRegex=re.compile(r'^([\d]+(\.[\d]+)?c)$'),
            defaultValue='0c'
        ),
        StyleAttribute(
            ns=itts_ns,
            nsIsRelative=False,
            tag='fillLineGap',
            appliesTo=['p'],
            syntaxRegex=re.compile(r'^(false)|(true)$'),
            defaultValue='false'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='origin',
            appliesTo=['region'],
            syntaxRegex=re.compile(
                r'^([\d]+(\.[\d]+)?%)[\s]+([\d]+(\.[\d]+)?%)$'),
            defaultValue='0% 0%'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='extent',
            appliesTo=['region'],
            syntaxRegex=re.compile(
                r'^([\d]+(\.[\d]+)?%)[\s]+([\d]+(\.[\d]+)?%)$'),
            defaultValue='100% 100%'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='displayAlign',
            appliesTo=['region'],  # Only on region in EBU-TT-D
            syntaxRegex=re.compile(
                r'^(before)|(center)|(after)$'),
            defaultValue='before'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='padding',
            appliesTo=['region'],  # Only on region in EBU-TT-D
            syntaxRegex=re.compile(
                r'^([\d]+(\.[\d]+)?%)([\s]+([\d]+(\.[\d]+)?%)){0-3}$'),
            defaultValue='0%'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='writingMode',
            appliesTo=['region'],
            syntaxRegex=re.compile(
                r'^(lrtb)|(rltb)|(tbrl)|(tblr)|(lr)|(rl)|(tb)$'),
            defaultValue='lrtb'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='showBackground',
            appliesTo=['region'],
            syntaxRegex=re.compile(
                r'^(always)|(whenActive)$'),
            defaultValue='always'
        ),
        StyleAttribute(
            ns=styling_ns_suffix,
            nsIsRelative=True,
            tag='overflow',
            appliesTo=['region'],
            syntaxRegex=re.compile(
                r'^(visible)|(hidden)$'),
            defaultValue='hidden'
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
            defaultValue=''
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


def getStyleAttributeKeys(tt_ns: str, elements: List[str]) -> List[str]:
    el_set = set(elements)
    return [_makeTag(tt_ns=tt_ns, styleAttribute=sa)
            for sa in styleAttribs
            if not el_set.isdisjoint(sa.appliesTo)]


def getStyleAttributeDict(
        tt_ns: str, elements: List[str]) -> Dict[str, StyleAttribute]:
    el_set = set(elements)
    return {_makeTag(tt_ns=tt_ns, styleAttribute=sa): sa
            for sa in styleAttribs
            if not el_set.isdisjoint(sa.appliesTo)}


def getAllStyleAttributeKeys(tt_ns: str) -> List[str]:
    return [_makeTag(tt_ns=tt_ns, styleAttribute=sa)
            for sa in styleAttribs]


def getAllStyleAttributeDict(tt_ns: str) -> Dict[str, StyleAttribute]:
    return {_makeTag(tt_ns=tt_ns, styleAttribute=sa): sa
            for sa in styleAttribs}


def attributeIsApplicableToElement(attr_key: str, el_tag: str) -> bool:
    return \
        attr_key not in _allAttributeKeys \
        or attr_key in _elementsToApplicableStyleAttributes.get(el_tag, set())
