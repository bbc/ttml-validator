from ..validationLogging.validationCodes import ValidationCode
from ..validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from ..xmlUtils import xmlIdAttr, make_qname
from .xmlCheck import XmlCheck
from .timingAttributeCheck import getTimingAttributes, \
    getParentTimingAttributes, pushParentTimingAttributes, \
    popParentTimingAttributes


class spanCheck(XmlCheck):
    """
    Checks the span element
    """

    _subChecks = []

    def __init__(self,
                 sub_checks: list[XmlCheck] = [],
                 require_text_in_span: bool = True,
                 permit_nested_spans: bool = False,
                 ):
        super().__init__()
        self._subChecks = sub_checks
        self._require_text_in_span = require_text_in_span
        self._permit_nested_spans = permit_nested_spans

    def run(self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        tt_ns = \
            context.get('root_ns', 'http://www.w3.org/ns/ttml')

        valid = True

        p_el_tag = make_qname(tt_ns, 'p')
        span_el_tag = make_qname(tt_ns, 'span')
        spans = [el for el in input if el.tag == span_el_tag]
        if self._require_text_in_span and \
           len(spans) == 0 and input.tag == p_el_tag:
            valid = False
            validation_results.error(
                location='{}/{} xml:id {}'.format(
                    input.tag,
                    span_el_tag,
                    input.get(xmlIdAttr, 'omitted'),
                ),
                message='Found 0 span elements; '
                        'text content needs to be in a styled span',
                code=ValidationCode.bbc_text_span_constraint
            )
        if not self._permit_nested_spans and \
           len(spans) > 0 and input.tag == span_el_tag:
            valid = False
            validation_results.error(
                location='{}/{} xml:id {}'.format(
                    input.tag,
                    span_el_tag,
                    input.get(xmlIdAttr, 'omitted'),
                ),
                message='Found {} span element children of span, require 0'
                        .format(len(spans)),
                code=ValidationCode.ebuttd_nested_span_constraint
            )

        timing_attributes = getTimingAttributes(el=input)
        parent_timing_attributes = getParentTimingAttributes(context=context)
        pushParentTimingAttributes(
            timing_attributes=parent_timing_attributes.union(
                timing_attributes),
            context=context,
            )
        for span in spans:
            for subCheck in self._subChecks:
                valid &= subCheck.run(
                    input=span,
                    context=context,
                    validation_results=validation_results
                )

            valid &= self.run(
                input=span,
                context=context,
                validation_results=validation_results
            )

        popParentTimingAttributes(context=context)

        return valid
