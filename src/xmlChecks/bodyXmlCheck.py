from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from src.xmlUtils import make_qname
from .ttmlUtils import ns_ttml
from .xmlCheck import XmlCheck
from .timingAttributeCheck import getTimingAttributes, \
    pushParentTimingAttributes, popParentTimingAttributes


class bodyCheck(XmlCheck):
    """
    Checks body element and content descendants
    """

    _subChecks = []

    def __init__(self,
                 sub_checks: list[XmlCheck] = []):
        super().__init__()
        self._subChecks = sub_checks

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        tt_ns = \
            context.get('root_ns', ns_ttml)
        body_el_tag = make_qname(tt_ns, 'body')

        valid = True

        bodys = [el for el in input if el.tag == body_el_tag]
        if len(bodys) == 0:
            validation_results.info(
                location='{}/{}'.format(input.tag, body_el_tag),
                message='No body elements present: empty document',
                code=ValidationCode.ttml_element_body
            )
        elif len(bodys) > 1:
            valid = False
            validation_results.error(
                location='{}/{}'.format(input.tag, body_el_tag),
                message='Found {} body elements, expected 1'.format(
                    len(bodys)),
                code=ValidationCode.ttml_element_body
            )
        else:
            body_el = bodys[0]
            timing_attributes = getTimingAttributes(body_el)
            pushParentTimingAttributes(
                timing_attributes=timing_attributes, context=context)
            for subCheck in self._subChecks:
                valid &= subCheck.run(
                    input=body_el,
                    context=context,
                    validation_results=validation_results
                )
            popParentTimingAttributes(context=context)

        if valid:
            validation_results.good(
                location='{}/{}'.format(input.tag, body_el_tag),
                message='Body checked',
                code=ValidationCode.ttml_element_body
            )

        return valid
