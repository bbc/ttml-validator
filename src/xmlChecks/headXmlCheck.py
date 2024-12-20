from typing import Dict, List
from ..validationResult import ValidationResult, ERROR, GOOD, WARN
from xml.etree.ElementTree import Element
from ..xmlUtils import make_qname, xmlIdAttr
from .xmlCheck import xmlCheck
from ..styleAttribs import getStyleAttributeKeys, getAllStyleAttributeDict


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

    def _validateStyleAttr(
            self,
            style_el: Element,
            context: Dict,
            validation_results: List[ValidationResult],
            tt_ns: str) -> bool:
        valid = True
        style_attr_dict = getAllStyleAttributeDict(tt_ns=tt_ns)
        for a_key, a_val in style_el.items():
            if a_key in style_attr_dict:
                match = style_attr_dict[a_key].syntaxRegex.match(a_val)
                if match is None:
                    valid = False
                    validation_results.append(
                        ValidationResult(
                            status=ERROR,
                            location='{}@{}'.format(
                                style_el.tag,
                                a_key),
                            message='Attribute value [{}] is invalid'.format(
                                a_val)
                        )
                    )

        return valid

    def _checkStyle(
            self,
            style_el: Element,
            context: Dict,
            validation_results: List[ValidationResult],
            tt_ns: str) -> bool:
        valid = True

        if xmlIdAttr not in style_el.keys():
            valid = False
            validation_results.append(ValidationResult(
                status=ERROR,
                location='{}@{}'.format(style_el.tag, xmlIdAttr),
                message='style element found with no xml:id'
            ))
        else:
            # Store in context for later use
            style_map = context.get('id_to_style_map', {})
            style_map[style_el.get(xmlIdAttr)] = style_el
            context['id_to_style_map'] = style_map

        # region-only style attributes should be inline in EBU-TT-D
        style_attr_keys = set(
            getStyleAttributeKeys(
                tt_ns=tt_ns,
                elements=['body', 'div', 'p', 'span']))
        if style_attr_keys.isdisjoint(style_el.keys()):
            validation_results.append(ValidationResult(
                status=WARN,
                location='{} {}'.format(
                    style_el.tag,
                    style_el.get(xmlIdAttr, '(no xml:id)')),
                message='Style element has no recognised style attributes'
            ))
        valid &= self._validateStyleAttr(style_el=style_el,
                                         context=context,
                                         validation_results=validation_results,
                                         tt_ns=tt_ns)

        return valid

    def _checkStyles(
            self,
            styling_el: Element,
            context: Dict,
            validation_results: List[ValidationResult],
            tt_ns: str) -> bool:
        style_el_tag = make_qname(tt_ns, 'style')
        valid = True

        style_els = [el for el in styling_el if el.tag == style_el_tag]
        if len(style_els) == 0:
            valid = False
            validation_results.append(ValidationResult(
                status=ERROR,
                location='{}/{}'.format(styling_el.tag, style_el_tag),
                message='At least one style element required, none found'
            ))
            context['id_to_style_map'] = {}  # expected downstream
        else:
            for style_el in style_els:
                valid &= self._checkStyle(
                    style_el=style_el,
                    context=context,
                    validation_results=validation_results,
                    tt_ns=tt_ns
                )

        if valid:
            validation_results.append(ValidationResult(
                status=GOOD,
                location='[{}/{}]'.format(styling_el.tag, style_el_tag),
                message='Style elements checked'
            ))

        return valid

    def _checkForStyling(
            self,
            head_el: Element,
            context: Dict,
            validation_results: List[ValidationResult],
            tt_ns: str) -> bool:
        styling_el_tag = make_qname(tt_ns, 'styling')

        styling_els = [el for el in head_el if el.tag == styling_el_tag]
        valid = True
        if len(styling_els) == 0:
            valid = False
            validation_results.append(ValidationResult(
                status=ERROR,
                location='{}/{}'.format(head_el.tag, styling_el_tag),
                message='Required styling element absent'
            ))
        elif len(styling_els) > 1:
            valid = False
            validation_results.append(ValidationResult(
                status=ERROR,
                location='{}/{}'.format(head_el.tag, styling_el_tag),
                message='{} styling elements found, expected 1'.format(
                    len(styling_els)
                )
            ))
        else:  # 1 styling element
            validation_results.append(ValidationResult(
                status=GOOD,
                location='{}/{}'.format(head_el.tag, styling_el_tag),
                message='styling element found'
                )
            )

        if not valid:
            validation_results.append(ValidationResult(
                status=WARN,
                location='{}/{}'.format(head_el.tag, styling_el_tag),
                message='Skipping style element checks'
                )
            )
        else:
            valid = self._checkStyles(
                styling_el=styling_els[0],
                context=context,
                validation_results=validation_results,
                tt_ns=tt_ns)

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
            valid &= self._checkForStyling(
                head_el=head_el,
                context=context,
                validation_results=validation_results,
                tt_ns=tt_ns)

        if valid:
            validation_results.append(ValidationResult(
                status=GOOD,
                location='{}/{}'.format(input.tag, head_el_tag),
                message='Head checked')
            )

        return valid
