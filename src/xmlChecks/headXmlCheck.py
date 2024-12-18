from typing import Dict, List
from ..validationResult import ValidationResult, ERROR, GOOD, WARN, INFO
from xml.etree.ElementTree import Element
from ..xmlUtils import get_namespace, get_unqualified_name, make_qname
from .xmlCheck import xmlCheck
import re


class headCheck(xmlCheck):
    """
    Checks presence of several elements in /tt/head.
    """

    def __init__(self, copyright_required: bool = False):
        super().__init__()
        self._copyright_required = copyright_required

    def _checkForCopyright(
            self,
            head_el: Element,
            context: Dict,
            validation_results: List[ValidationResult],
            ttm_ns: str) -> bool:
        copyright_el_tag = make_qname(ttm_ns, 'copyright')
        copyright_els = [el for el in head_el if el.tag == copyright_el_tag]
        valid = True
        if len(copyright_els) == 0:
            valid = not self._copyright_required
            validation_results.append(ValidationResult(
                status=ERROR if self._copyright_required else WARN,
                location='{}/{}'.format(head_el.tag, copyright_el_tag),
                message='{}copyright element absent'.format(
                        'Required ' if self._copyright_required else ''
                    )
            ))
        elif len(copyright_els) > 1:
            validation_results.append(ValidationResult(
                status=WARN,
                location='{}/{}'.format(head_el.tag, copyright_el_tag),
                message='{} copyright elements found, expected 1'.format(
                    len(copyright_els)
                )
            ))
        else:  # 1 copyright element
            validation_results.append(ValidationResult(
                status=GOOD,
                location='{}/{}'.format(head_el.tag, copyright_el_tag),
                message='Copyright element found'
                )
            )
        return valid

    def run(
            self,
            input: Element,
            context: Dict,
            validation_results: List[ValidationResult]) -> bool:
        tt_ns = \
            context.get('root_ns', 'http://www.w3.org/ns/ttml')
        head_el_tag = make_qname(tt_ns, 'head')
        ttm_ns = tt_ns + '#metadata'
        styling_el_tag = make_qname(tt_ns, 'styling')
        style_el_tag = make_qname(tt_ns, 'style')

        valid = True

        heads = [el for el in input if el.tag == head_el_tag]
        if len(heads) != 1:
            validation_results.append(ValidationResult(
                status=ERROR,
                location='{}/{}'.format(input.tag, head_el_tag),
                message='Found {} head elements, expected 1'.format(len(heads))
            ))
            valid = False
        else:
            head_el = heads[0]
            valid &= self._checkForCopyright(
                head_el=head_el,
                context=context,
                validation_results=validation_results,
                ttm_ns=ttm_ns)

        if valid:
            validation_results.append(ValidationResult(
                status=GOOD,
                location='{}/{}'.format(input.tag, head_el_tag),
                message='Head checked')
            )

        return valid
