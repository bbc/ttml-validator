from ..validationResult import ValidationResult, ERROR, GOOD, WARN, INFO
from xml.etree.ElementTree import Element
from ..xmlUtils import get_namespace, get_unqualified_name, make_qname, \
    xmlIdAttr
from .xmlCheck import xmlCheck
import re

timing_attr_keys = set([
    'begin',
    'end',
    'dur'
])

class bodyCheck(xmlCheck):
    """
    Checks body element and content descendants
    """

    def _checkNoTimingAttributes(
            self,
            el: Element,
            validation_results: list[ValidationResult],
    ) -> bool:
        valid = True

        attr_key_set = set(el.keys())
        if not attr_key_set.isdisjoint(timing_attr_keys):
            valid = False
            validation_results.append(ValidationResult(
                status=ERROR,
                location='{} element xml:id {}'
                         .format(el.tag, el.get(xmlIdAttr, 'omitted')),
                message='Prohibited timing attributes {} present'
                        .format(attr_key_set.intersection(timing_attr_keys))
            ))

        return valid

    def _checkSpanChildren(
            self,
            parent_el: Element,
            context: dict,
            validation_results: list[ValidationResult],
            tt_ns: str,
    ) -> bool:
        valid = True

        p_el_tag = make_qname(tt_ns, 'p')
        span_el_tag = make_qname(tt_ns, 'span')
        spans = [el for el in parent_el if el.tag == span_el_tag]
        if len(spans) == 0 and parent_el.tag == p_el_tag:
            valid = False
            validation_results.append(ValidationResult(
                status=WARN,
                location='{}/{} xml:id {}'.format(
                    parent_el.tag,
                    span_el_tag,
                    parent_el.get(xmlIdAttr, 'omitted'),
                ),
                message='Found 0 span elements; '
                        'text content needs to be in a styled span'
            ))
        if len(spans) > 0 and parent_el.tag == span_el_tag:
            valid = False
            validation_results.append(ValidationResult(
                status=ERROR,
                location='{}/{} xml:id {}'.format(
                    parent_el.tag,
                    span_el_tag,
                    parent_el.get(xmlIdAttr, 'omitted'),
                ),
                message='Found {} span element children of span, require 0'
                        .format(len(spans))
            ))

        for span in spans:
            valid &= self._checkSpanChildren(
                parent_el=span,
                context=context,
                validation_results=validation_results,
                tt_ns=tt_ns,
            )

        return valid

    def _checkNoTextChildren(
            self,
            el: Element,
            context: dict,
            validation_results: list[ValidationResult],
    ) -> bool:
        valid = True

        text_children_present = el.text is not None  # and el.text != ''
        for child_el in el:
            text_children_present |= child_el.tail is not None  # and el.tail != ''

        if text_children_present:
            valid = False
            validation_results.append(ValidationResult(
                status=ERROR,
                location='{} element xml:id {}'.format(
                    el.tag,
                    el.get(xmlIdAttr, 'omitted')),
                message='Text content found in prohibited location.'
            ))

        return valid

    def _checkPChildren(
            self,
            parent_el: Element,
            context: dict,
            validation_results: list[ValidationResult],
            tt_ns: str,
    ) -> bool:
        valid = True

        p_el_tag = make_qname(tt_ns, 'p')
        ps = [el for el in parent_el if el.tag == p_el_tag]
        if len(ps) == 0:
            valid = False
            validation_results.append(ValidationResult(
                status=ERROR,
                location='{}/{} xml:id {}'.format(
                    parent_el.tag,
                    p_el_tag,
                    parent_el.get(xmlIdAttr, 'omitted'),
                ),
                message='Found 0 p children of a div, require >0')
            )

        for p in ps:
            if xmlIdAttr not in p.keys():
                valid = False
                validation_results.append(ValidationResult(
                    status=ERROR,
                    location='{}/{} xml:id {}'.format(
                        parent_el.tag,
                        p_el_tag,
                        p.get(xmlIdAttr, 'omitted'),
                    ),
                    message='p element missing required xml:id')
                )
            valid &= self._checkNoTextChildren(
                el=p,
                context=context,
                validation_results=validation_results,
            )
            valid &= self._checkSpanChildren(
                parent_el=p,
                context=context,
                validation_results=validation_results,
                tt_ns=tt_ns
            )

        return valid

    def _checkDivChildren(
            self,
            parent_el: Element,
            context: dict,
            validation_results: list[ValidationResult],
            tt_ns: str,
    ) -> bool:
        valid = True

        div_el_tag = make_qname(tt_ns, 'div')
        divs = [el for el in parent_el if el.tag == div_el_tag]
        if len(divs) == 0 and get_unqualified_name(parent_el.tag) == 'body':
            valid = False
            validation_results.append(ValidationResult(
                status=ERROR,
                location='{}/{}'.format(parent_el.tag, div_el_tag),
                message='Found 0 div elements, require >0')
            )
        elif len(divs) > 0 and get_unqualified_name(parent_el.tag) == 'div':
            valid = False
            validation_results.append(ValidationResult(
                status=ERROR,
                location='{}/{}'.format(parent_el.tag, div_el_tag),
                message='Found {} div children of a div, require 0'
                        .format(len(divs)))
            )

        # Check each div child
        for div in divs:
            valid &= self._checkNoTimingAttributes(
                el=div,
                validation_results=validation_results,
            )
            valid &= self._checkDivChildren(
                parent_el=div,
                context=context,
                validation_results=validation_results,
                tt_ns=tt_ns,
            )
            valid &= self._checkPChildren(
                parent_el=div,
                context=context,
                validation_results=validation_results,
                tt_ns=tt_ns,
            )

        return valid

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: list[ValidationResult]) -> bool:
        tt_ns = \
            context.get('root_ns', 'http://www.w3.org/ns/ttml')
        body_el_tag = make_qname(tt_ns, 'body')

        valid = True

        bodys = [el for el in input if el.tag == body_el_tag]
        if len(bodys) != 1:
            valid = False
            validation_results.append(ValidationResult(
                status=ERROR,
                location='{}/{}'.format(input.tag, body_el_tag),
                message='Found {} body elements, expected 1'.format(len(bodys))
            ))
        else:
            body_el = bodys[0]
            valid &= self._checkNoTimingAttributes(
                el=body_el,
                validation_results=validation_results,
            )
            valid &= self._checkDivChildren(
                parent_el=body_el,
                context=context,
                validation_results=validation_results,
                tt_ns=tt_ns)

        if valid:
            validation_results.append(ValidationResult(
                status=GOOD,
                location='{}/{}'.format(input.tag, body_el_tag),
                message='Body checked')
            )

        return valid
