from ..validationLogging.validationCodes import ValidationCode
from ..validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from ..xmlUtils import make_qname,  \
    xmlIdAttr
from .xmlCheck import XmlCheck


class noTextChildren(XmlCheck):
    """
    Checks that element has no text children
    """

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:

        valid = True

        text_children_present = input.text is not None
        for child_el in input:
            text_children_present |= child_el.tail is not None

        if text_children_present:
            valid = False
            validation_results.error(
                location='{} element xml:id {}'.format(
                    input.tag,
                    input.get(xmlIdAttr, 'omitted')),
                message='Text content found in prohibited location.',
                code=ValidationCode.bbc_text_span_constraint
            )

        return valid


class checkLineBreaks(XmlCheck):
    """
    Checks for line breaks instead of <br> elements
    """

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:

        valid = True

        tt_ns = \
            context.get('root_ns', 'http://www.w3.org/ns/ttml')
        all_text = "".join(input.itertext())
        br_tag = make_qname(tt_ns, 'br')
        br_subelements = input.findall('.//'+br_tag)
        lines = all_text.splitlines()

        if len(lines) > 1 and len(br_subelements) == 0:
            validation_results.warn(
                location='{} element xml:id {}'.format(
                    input.tag,
                    input.get(xmlIdAttr, 'omitted')),
                message='Text content contains line breaks '
                        'but no <br> elements.',
                code=ValidationCode.ttml_element_br
            )

        return valid
