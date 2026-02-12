# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from src.xmlUtils import make_qname, xmlIdAttr
from .xmlCheck import XmlCheck
from .ttmlUtils import ns_ttml
from src.styleAttribs import getAllStyleAttributeKeys


class inlineStyleAttributesCheck(XmlCheck):
    """
    Checks for inline style attributes on body, div, p and span.
    """
    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        valid = True
        tt_ns = \
            context.get('root_ns', ns_ttml)
        style_attribute_keys = set(getAllStyleAttributeKeys(tt_ns=tt_ns))
        style_attribute_keys.remove('style')  # the one that is allowed!
        el_tags = set(make_qname(tt_ns, t)
                      for t in
                      ['body', 'div', 'p', 'span'])
        for el in input.iter():
            if el.tag in el_tags:
                for attr in el.keys():
                    if attr in style_attribute_keys:
                        valid = False
                        validation_results.error(
                            location='{} xml:id={}'.format(
                                el.tag,
                                el.get(xmlIdAttr, '[absent]')),
                            message='Inline style attribute {} '
                                    'not permitted on content element'
                                    .format(attr),
                            code=ValidationCode
                                    .ebuttd_inline_styling_constraint
                        )

        if valid:
            validation_results.good(
                location='content elements',
                message='Inline style attributes checked',
                code=ValidationCode.ttml_attribute_styling_attribute
            )

        return valid
