from ..validationLogging.validationCodes import ValidationCode
from ..validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from ..xmlUtils import make_qname, xmlIdAttr
from .xmlCheck import XmlCheck
from ..styleAttribs import getStyleAttributeKeys, validateStyleAttr


class layoutCheck(XmlCheck):
    """
    Checks presence and contents of layout element
    """

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        tt_ns = context.get('root_ns', 'http://www.w3.org/ns/ttml')
        layout_el_tag = make_qname(tt_ns, 'layout')

        layout_els = [el for el in input if el.tag == layout_el_tag]
        valid = True
        if len(layout_els) == 0:
            valid = False
            validation_results.error(
                location='{}/{}'.format(input.tag, layout_el_tag),
                message='Required layout element absent',
                code=ValidationCode.ebuttd_layout_element_constraint
            )
        elif len(layout_els) > 1:
            valid = False
            validation_results.error(
                location='{}/{}'.format(input.tag, layout_el_tag),
                message='{} layout elements found, expected 1'.format(
                    len(layout_els)),
                code=ValidationCode.ttml_element_layout
            )
        else:  # 1 layout element
            validation_results.good(
                location='{}/{}'.format(input.tag, layout_el_tag),
                message='layout element found',
                code=ValidationCode.ebuttd_layout_element_constraint
            )

        if not valid:
            validation_results.skip(
                location='{}/{}'.format(input.tag, layout_el_tag),
                message='Skipping region element checks',
                code=ValidationCode.ttml_element_region
            )
        else:
            valid = self._checkRegions(
                layout_el=layout_els[0],
                context=context,
                validation_results=validation_results)

        return valid

    def _checkRegion(
            self,
            region_el: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        valid = True
        tt_ns = context.get('root_ns', 'http://www.w3.org/ns/ttml')

        if xmlIdAttr not in region_el.keys():
            valid = False
            validation_results.error(
                location='{}@{}'.format(region_el.tag, xmlIdAttr),
                message='region element found with no xml:id',
                code=ValidationCode.ttml_element_region
            )
        else:
            # Store in context for later use
            region_map = context.get('id_to_region_map', {})
            region_map[region_el.get(xmlIdAttr)] = region_el
            context['id_to_region_map'] = region_map

        # region-only style attributes should be inline in EBU-TT-D
        style_attr_keys = set(
            getStyleAttributeKeys(
                tt_ns=tt_ns,
                elements=['region']))
        if style_attr_keys.isdisjoint(region_el.keys()):
            validation_results.warn(
                location='{} {}'.format(
                    region_el.tag,
                    region_el.get(xmlIdAttr, '(no xml:id)')),
                message='Region element has no recognised style attributes',
                code=ValidationCode.ttml_element_region
            )
        valid &= validateStyleAttr(style_el=region_el,
                                   context=context,
                                   validation_results=validation_results)

        return valid

    def _checkRegions(
            self,
            layout_el: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        tt_ns = context.get('root_ns', 'http://www.w3.org/ns/ttml')
        region_el_tag = make_qname(tt_ns, 'region')
        valid = True

        region_els = [el for el in layout_el if el.tag == region_el_tag]
        if len(region_els) == 0:
            valid = False
            validation_results.error(
                location='{}/{}'.format(layout_el.tag, region_el_tag),
                message='At least one region element required, none found',
                code=ValidationCode.ebuttd_region_element_constraint
            )
            context['id_to_region_map'] = {}  # expected downstream
        else:
            for region_el in region_els:
                valid &= self._checkRegion(
                    region_el=region_el,
                    context=context,
                    validation_results=validation_results
                )

        if valid:
            validation_results.good(
                location='[{}/{}]'.format(layout_el.tag, region_el_tag),
                message='Region elements checked',
                code=ValidationCode.ttml_element_layout
            )

        return valid
