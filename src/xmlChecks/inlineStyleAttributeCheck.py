from ..validationLogging.validationResult import ValidationResult, ERROR, GOOD
from xml.etree.ElementTree import Element
from ..xmlUtils import make_qname, xmlIdAttr
from .xmlCheck import xmlCheck
from ..styleAttribs import getAllStyleAttributeKeys


class inlineStyleAttributesCheck(xmlCheck):
    """
    Checks for inline style attributes on body, div, p and span.
    """
    def run(
            self,
            input: Element,
            context: dict,
            validation_results: list[ValidationResult]) -> bool:
        valid = True
        tt_ns = \
            context.get('root_ns', 'http://www.w3.org/ns/ttml')
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
                        validation_results.append(
                            ValidationResult(
                                status=ERROR,
                                location='{} xml:id={}'.format(
                                    el.tag,
                                    el.get(xmlIdAttr, '[absent]')),
                                message='Inline style attribute {} '
                                        'not permitted on content element'
                                        .format(attr)
                            )
                        )

        if valid:
            validation_results.append(
                ValidationResult(
                    status=GOOD,
                    location='content elements',
                    message='Inline style attributes checked'
                )
            )

        return valid
