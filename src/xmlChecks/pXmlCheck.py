# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from src.xmlUtils import xmlIdAttr, make_qname
from .xmlCheck import XmlCheck
from .ttmlUtils import ns_ttml
from .timingAttributeCheck import getTimingAttributes, \
    pushParentTimingAttributes, popParentTimingAttributes


class pCheck(XmlCheck):
    """
    Checks the p element
    """

    _subChecks = []

    def __init__(self,
                 sub_checks: list[XmlCheck] = []):
        super().__init__()
        self._subChecks = sub_checks

    def run(self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        tt_ns = \
            context.get('root_ns', ns_ttml)

        valid = True

        p_el_tag = make_qname(tt_ns, 'p')
        ps = [el for el in input if el.tag == p_el_tag]
        if len(ps) == 0:
            valid = False
            validation_results.error(
                location='{}/{} xml:id {}'.format(
                    input.tag,
                    p_el_tag,
                    input.get(xmlIdAttr, 'omitted'),
                ),
                message='Found 0 p children of a div, require >0',
                code=ValidationCode.ebuttd_empty_div_constraint
            )

        for p in ps:
            timing_attributes = getTimingAttributes(el=p)
            pushParentTimingAttributes(
                timing_attributes=timing_attributes,
                context=context)
            for subCheck in self._subChecks:
                valid &= subCheck.run(
                    input=p,
                    context=context,
                    validation_results=validation_results
                )
            popParentTimingAttributes(context=context)

        return valid
