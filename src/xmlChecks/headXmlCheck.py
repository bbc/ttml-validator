from ..validationLogging.validationCodes import ValidationCode
from ..validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from ..xmlUtils import make_qname
from .xmlCheck import XmlCheck


class headCheck(XmlCheck):
    """
    Checks presence of several elements in /tt/head.
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
            context.get('root_ns', 'http://www.w3.org/ns/ttml')
        head_el_tag = make_qname(tt_ns, 'head')

        valid = True

        heads = [el for el in input if el.tag == head_el_tag]
        if len(heads) < 1:
            valid = False
            validation_results.error(
                location='{}/{}'.format(input.tag, head_el_tag),
                message='Found {} head elements, expected 1'
                        .format(len(heads)),
                code=ValidationCode.ebuttd_head_element_constraint
            )
        elif len(heads) > 1:
            valid = False
            validation_results.error(
                location='{}/{}'.format(input.tag, head_el_tag),
                message='Found {} head elements, expected 1'
                        .format(len(heads)),
                code=ValidationCode.ttml_element_head
            )
        else:
            head_el = heads[0]
            for subCheck in self._subChecks:
                valid &= subCheck.run(
                    input=head_el,
                    context=context,
                    validation_results=validation_results
                )

        if valid:
            validation_results.good(
                location='{}/{}'.format(input.tag, head_el_tag),
                message='Head checked',
                code=ValidationCode.ttml_element_head)

        return valid
