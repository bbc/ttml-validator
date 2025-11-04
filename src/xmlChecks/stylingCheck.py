from ..validationLogging.validationCodes import ValidationCode
from ..validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from ..xmlUtils import make_qname, xmlIdAttr
from .xmlCheck import XmlCheck
from .ttmlUtils import ns_ttml
from ..styleAttribs import getStyleAttributeKeys, validateStyleAttr


class stylingCheck(XmlCheck):
    """
    Checks presence and contents of styling element
    """

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:

        tt_ns = context.get('root_ns', ns_ttml)
        styling_el_tag = make_qname(tt_ns, 'styling')

        styling_els = [el for el in input if el.tag == styling_el_tag]
        valid = True
        if len(styling_els) == 0:
            valid = False
            validation_results.error(
                location='{}/{}'.format(input.tag, styling_el_tag),
                message='Required styling element absent',
                code=ValidationCode.ebuttd_styling_element_constraint
            )
        elif len(styling_els) > 1:
            valid = False
            validation_results.error(
                location='{}/{}'.format(input.tag, styling_el_tag),
                message='{} styling elements found, expected 1'.format(
                    len(styling_els)),
                code=ValidationCode.ttml_element_styling
            )
        else:  # 1 styling element
            validation_results.good(
                location='{}/{}'.format(input.tag, styling_el_tag),
                message='styling element found',
                code=ValidationCode.ebuttd_styling_element_constraint
            )

        if not valid:
            validation_results.skip(
                location='{}/{}'.format(input.tag, styling_el_tag),
                message='Skipping style element checks',
                code=ValidationCode.ttml_element_style
            )
        else:
            valid = self._checkStyles(
                styling_el=styling_els[0],
                context=context,
                validation_results=validation_results)

        return valid

    def _checkStyle(
            self,
            style_el: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        valid = True
        tt_ns = context.get('root_ns', ns_ttml)

        if xmlIdAttr not in style_el.keys():
            valid = False
            validation_results.error(
                location='{}@{}'.format(style_el.tag, xmlIdAttr),
                message='style element found with no xml:id',
                code=ValidationCode.ttml_element_style
            )
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
            validation_results.warn(
                location='{} {}'.format(
                    style_el.tag,
                    style_el.get(xmlIdAttr, '(no xml:id)')),
                message='Style element has no recognised style attributes',
                code=ValidationCode.ttml_element_style
            )
        valid &= validateStyleAttr(style_el=style_el,
                                   context=context,
                                   validation_results=validation_results)

        return valid

    def _checkStyles(
            self,
            styling_el: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        tt_ns = context.get('root_ns', ns_ttml)
        style_el_tag = make_qname(tt_ns, 'style')
        valid = True

        style_els = [el for el in styling_el if el.tag == style_el_tag]
        if len(style_els) == 0:
            valid = False
            validation_results.error(
                location='{}/{}'.format(styling_el.tag, style_el_tag),
                message='At least one style element required, none found',
                code=ValidationCode.ebuttd_style_element_constraint
            )
            context['id_to_style_map'] = {}  # expected downstream
        else:
            for style_el in style_els:
                valid &= self._checkStyle(
                    style_el=style_el,
                    context=context,
                    validation_results=validation_results
                )
            if 'id_to_style_map' not in context:
                context['id_to_style_map'] = {}

        if valid:
            validation_results.good(
                location='[{}/{}]'.format(styling_el.tag, style_el_tag),
                message='Style elements checked',
                code=ValidationCode.ttml_element_styling
            )

        return valid
