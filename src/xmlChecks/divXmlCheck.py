# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from src.xmlUtils import make_qname, get_unqualified_name
from .xmlCheck import XmlCheck
from .ttmlUtils import ns_ttml
from .timingAttributeCheck import getTimingAttributes, \
    pushParentTimingAttributes, popParentTimingAttributes


class divCheck(XmlCheck):
    """
    Checks the div element
    """

    _subChecks = []

    def __init__(self,
                 sub_checks: list[XmlCheck] = [],
                 recurse_div_children: bool = True):
        super().__init__()
        self._subChecks = sub_checks
        self._recurse_div_children = recurse_div_children

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        tt_ns = \
            context.get('root_ns', ns_ttml)

        valid = True

        div_el_tag = make_qname(tt_ns, 'div')
        divs = [el for el in input if el.tag == div_el_tag]
        if len(divs) == 0 and get_unqualified_name(input.tag) == 'body':
            valid = False
            validation_results.error(
                location='{}/{}'.format(input.tag, div_el_tag),
                message='Found 0 div elements, require >0',
                code=ValidationCode.ebuttd_empty_body_constraint
            )
        elif len(divs) > 0 and get_unqualified_name(input.tag) == 'div':
            valid = False
            validation_results.error(
                location='{}/{}'.format(input.tag, div_el_tag),
                message='Found {} div children of a div, require 0'
                        .format(len(divs)),
                code=ValidationCode.ebuttd_nested_div_constraint
            )

        # Check each div child
        for div in divs:
            timing_attributes = getTimingAttributes(div)
            pushParentTimingAttributes(
                timing_attributes=timing_attributes, context=context)
            if self._recurse_div_children:
                valid &= self.run(
                    input=div,
                    context=context,
                    validation_results=validation_results
                )
            for subCheck in self._subChecks:
                valid &= subCheck.run(
                    input=div,
                    context=context,
                    validation_results=validation_results
                )
            popParentTimingAttributes(context=context)

        return valid
