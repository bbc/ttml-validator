# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from src.xmlUtils import make_qname, xmlIdAttr, get_unqualified_name
from .xmlCheck import XmlCheck
from .ttmlUtils import ns_ttml
from src.styleAttribs import getAllStyleAttributeDict, \
    attributeIsApplicableToElement, \
    canonicaliseFontFamily, computeStyles, getMergedStyleSet
import logging


permitted_color_values = [
    '#ffffff',   # white
    '#ffffffff',
    '#00ffff',   # cyan
    '#00ffffff',
    '#ffff00',   # yellow
    '#ffff00ff',
    '#00ff00',   # green
    '#00ff00ff',
]

permitted_span_backgroundColor_values = [
    '#000000',
    '#000000ff'
]


class styleRefsXmlCheck(XmlCheck):
    """
    Checks for unreferenced styles and inappropriate style attributes.
    """

    def _gather_style_refs(
            self,
            input: Element,
    ) -> dict[str, list[Element]]:
        style_to_referencing_el_map = {}
        style_attr_key = 'style'
        for el in input.iter():
            if style_attr_key in el.keys():
                style_refs = el.get(style_attr_key).split()
                for style_ref in style_refs:
                    referencing_el_list = \
                        style_to_referencing_el_map.get(style_ref, [])
                    referencing_el_list.append(el)
                    style_to_referencing_el_map[style_ref] =\
                        referencing_el_list

        return style_to_referencing_el_map

    def _get_style_attrib_map(
            self,
            style_el: Element,
            id_to_style_map: dict[str, Element],
            style_attrib_map: dict[str, str],
            visited_styles: list[str],
            validation_results: ValidationLogger,
            ) -> bool:
        valid = True
        style_refs = style_el.get('style', '').split()
        for style_ref in style_refs:
            if style_ref not in visited_styles:
                visited_styles.append(style_ref)
                valid &= self._get_style_attrib_map(
                    id_to_style_map[style_ref],
                    id_to_style_map=id_to_style_map,
                    style_attrib_map=style_attrib_map,
                    visited_styles=visited_styles,
                    validation_results=validation_results
                )
            else:
                validation_results.error(
                    location='style element',
                    message='Cyclic style ref to {} found'.format(
                        style_ref),
                    code=ValidationCode.ttml_styling_referential_chained
                )
                valid = False

        for key, value in style_el.items():
            if key != 'style':
                style_attrib_map[key] = value

        return valid

    def _gather_style_attribs(
            self,
            id_to_style_map: dict[str, Element],
            validation_results: ValidationLogger,
            id_to_styleattribs_map: dict[str, dict[str, str]],
            ) -> bool:
        valid = True

        for id, style_el in id_to_style_map.items():
            attrib_map = {}
            visited = []
            valid &= self._get_style_attrib_map(
                style_el=style_el,
                id_to_style_map=id_to_style_map,
                style_attrib_map=attrib_map,
                visited_styles=visited,
                validation_results=validation_results
            )

            id_to_styleattribs_map[id] = attrib_map

        return valid

    def _check_attr_applicability(
            self,
            tag: str,
            sss: dict,
            validation_results: ValidationLogger
            ) -> bool:
        valid = True

        for attr_key in sss.keys():
            if not attributeIsApplicableToElement(
                    attr_key=get_unqualified_name(
                        attr_key), el_tag=tag):
                valid = False
                validation_results.error(
                    location='{} element'.format(tag),
                    message='Specified style attribute {} is not '
                            'applicable to element type {}'
                            .format(attr_key, tag),
                    code=ValidationCode.ttml_styling_attribute_applicability
                    )

        return valid

    def _check_no_backgroundColor(
            self,
            sss: dict[str, str],
            el_tag: str,
            tt_ns: str,
            validation_results: ValidationLogger
            ) -> bool:
        valid = True

        style_attrib_dict = getAllStyleAttributeDict(
            tt_ns=tt_ns)
        for style_attr_key, style_attr in style_attrib_dict.items():
            unq_attr_key = get_unqualified_name(style_attr_key)
            if unq_attr_key == 'backgroundColor' \
               and style_attr_key in sss:
                backgroundColor_val = sss[style_attr_key]
                parsed_bg = style_attr.syntaxRegex.fullmatch(
                                backgroundColor_val)
                if parsed_bg is None:
                    valid = False
                    validation_results.error(
                        location='{} element {} attribute'
                                 .format(el_tag, style_attr_key),
                        message='backgroundColor attribute {} '
                                'is not valid'
                                .format(backgroundColor_val),
                        code=ValidationCode.ttml_attribute_styling_attribute
                    )
                else:
                    a = int(parsed_bg.group('a'), 16) \
                        if parsed_bg.group('a') else 255
                    if a != 0:
                        valid = False
                        validation_results.error(
                            location='{} element {} attribute'
                                     .format(
                                        el_tag,
                                        style_attr_key),
                            message='backgroundColor {} is not '
                                    'transparent (BBC requirement)'
                                    .format(backgroundColor_val),
                            code=ValidationCode
                                    .bbc_block_backgroundColor_constraint
                        )

        return valid

    def _getFontSizeMinMax(self, context: dict) -> tuple[float, float]:
        min_fs = 6
        max_fs = 7.5

        if context.get('args', {}).get('vertical', False):
            min_fs = 3
            max_fs = 4.5

        return (min_fs, max_fs)

    def _check_styles(
                    self,
                    el: Element,
                    context: dict,
                    validation_results: ValidationLogger,
                    tt_ns: str,
                    parent_css: dict) -> bool:
        valid = True

        el_tag = get_unqualified_name(el.tag)
        validation_location = \
            '{} element xml:id {}'.format(
                el_tag, el.get(xmlIdAttr, 'omitted'))

        id_to_styleattribs_map = context['id_to_style_attribs_map']

        # Iterate through the elements from body down to span
        # For each, gather the specified style set
        # and compute the computed styles, then pass the
        # computed style set down to each child to compute
        # its style set.
        el_sss = getMergedStyleSet(
            el=el,
            id_to_styleattribs_map=id_to_styleattribs_map
        )

        # For all references from span elements, check that the referenced
        # attributes apply to span, and ERROR for any that do not.
        if el_tag == 'span':
            valid &= self._check_attr_applicability(
                tag=el_tag,
                sss=el_sss,
                validation_results=validation_results)

        # For all references from elements other than span, check that
        # there is no non-transparent tts:backgroundColor attribute
        # (BBC requirement) - if there is, ERROR
        if el_tag in ['region', 'body', 'div', 'p']:
            valid &= self._check_no_backgroundColor(
                sss=el_sss,
                el_tag=el_tag,
                tt_ns=tt_ns,
                validation_results=validation_results)

        # Generate the computed style set
        el_css = {}
        params = {}
        cell_resolution_key = 'cellResolution'
        if cell_resolution_key in context:
            params[cell_resolution_key] = context[cell_resolution_key]

        valid &= computeStyles(
            tt_ns=tt_ns,
            validation_results=validation_results,
            el_sss=el_sss,
            el_css=el_css,
            parent_css=parent_css,
            params=params
        )

        min_fs, max_fs = self._getFontSizeMinMax(context=context)
        min_lh = 1.2 * min_fs
        max_lh = 1.2 * max_fs

        if el_tag in ['p', 'span']:
            # Check for referenced style lists that have wrong computed
            # tts:fontFamily value (BBC requirement) - if there is, ERROR
            c_font_family = canonicaliseFontFamily(
                el_css.get('fontFamily', 'default'))
            required_font_family = canonicaliseFontFamily(
                'ReithSans, Arial, Roboto, proportionalSansSerif, default')
            if c_font_family != required_font_family:
                valid = False
                validation_results.error(
                    location=validation_location,
                    message='Computed fontFamily {} differs'
                            ' from BBC requirement'
                            .format(c_font_family),
                    code=ValidationCode.bbc_text_fontFamily_constraint
                )

            # Compute fontSize for every p and span,
            # and check it is within BBC range 2% - 8%
            # ERROR if not
            c_font_size = el_css.get('fontSize', '')
            if c_font_size[-2:] != 'rh':
                raise RuntimeError(
                    'Non-canonical computed fontSize {}'.format(c_font_size))
            c_font_size_val = float(c_font_size[:-2])
            if c_font_size_val < min_fs or c_font_size_val > max_fs:
                valid = False
                validation_results.error(
                    location=validation_location,
                    message='Computed fontSize {:.3f}rh outside '
                            'BBC-allowed range {}rh-{}rh'
                            .format(c_font_size_val, min_fs, max_fs),
                    code=ValidationCode.bbc_text_fontSize_constraint
                )
            else:
                validation_results.good(
                    location=validation_location,
                    message='Computed fontSize {:.3f}rh '
                            '(within BBC-allowed range)'
                            .format(c_font_size_val),
                    code=ValidationCode.bbc_text_fontSize_constraint
                )

        # Compute lineHeight for every p, ERROR if <100% or >130%,
        # WARN if "normal"
        if el_tag == 'p':
            c_line_height = el_css.get('lineHeight', 'broken')
            # print('lineHeight = {}'.format(c_line_height))

            if c_line_height == 'normal':
                validation_results.warn(
                    location=validation_location,
                    message='lineHeight normal used - '
                            'SHOULD use explicit percentage',
                    code=ValidationCode.bbc_text_lineHeight_constraint
                )
            else:
                if c_line_height[-2:] != 'rh':
                    raise RuntimeError(
                        'Non-canonical computed lineHeight {}'.format(
                            c_line_height))
                c_line_height_val = float(c_line_height[:-2])
                if c_line_height_val < min_lh \
                   or c_line_height_val > max_lh:
                    valid = False
                    validation_results.error(
                        location=validation_location,
                        message='Computed lineHeight {:.3f}rh outside '
                                'BBC-allowed range {:.3f}rh-{:.3f}rh'
                                .format(c_line_height_val, min_lh, max_lh),
                        code=ValidationCode.bbc_text_lineHeight_constraint
                    )

            # For every p, check if ebutts:multiRowAlign is present (INFO) and
            # if not auto and different from tts:textAlign,
            # WARN (BBC requirement)
            c_ta = el_css.get('textAlign')
            c_mra = el_css.get('multiRowAlign')
            # print('multiRowAlign = {}, textAlign = {}'.format(c_mra, c_ta))
            if c_mra != 'auto' and c_mra == c_ta:
                validation_results.info(
                    location=validation_location,
                    message='Computed multiRowAlign set to {}, '
                            'matches textAlign'
                            .format(c_mra),
                    code=ValidationCode.ebuttd_multiRowAlign
                )
            elif c_mra != 'auto':
                validation_results.warn(
                    location=validation_location,
                    message='Computed multiRowAlign set to {}, '
                            'differs from textAlign {} '
                            '(Not expected in BBC requirements)'
                            .format(c_mra, c_ta),
                    code=ValidationCode.bbc_text_multiRowAlign_constraint
                )

            # For every p, check ebutts:linePadding - ERROR if absent,
            # ERROR if out of range
            c_lp = el_css.get('linePadding')
            # print('linePadding = {}'.format(c_lp))

            if c_lp[-1:] != 'c':
                raise RuntimeError(
                    'Non-canonical computed linePadding {}'.format(c_lp))
            c_lp_val = float(c_lp[:-1])
            if c_lp_val < 0.3 or c_lp_val > 0.8:
                valid = False
                validation_results.error(
                    location=validation_location,
                    message='Computed linePadding {} outside BBC-allowed range'
                            .format(c_lp),
                    code=ValidationCode.bbc_text_linePadding_constraint
                )
            else:
                validation_results.good(
                    location=validation_location,
                    message='Computed linePadding {} within BBC-allowed range'
                            .format(c_lp),
                    code=ValidationCode.bbc_text_linePadding_constraint
                )

            # For every p, check itts:fillLineGap - ERROR if not true
            c_flg = el_css.get('fillLineGap')
            # print('fillLineGap = {}'.format(c_flg))
            if c_flg != 'true':
                valid = False
                validation_results.error(
                    location=validation_location,
                    message='Computed fillLineGap {} not BBC-allowed value'
                            .format(c_flg),
                    code=ValidationCode.bbc_text_fillLineGap_constraint
                )

        if el_tag == 'span':
            # For every span, check tts:color - ERROR if not a permitted color
            c_c = el_css.get('color').lower()
            # print('color = {}'.format(c_c))

            if c_c not in permitted_color_values:
                valid = False
                validation_results.error(
                    location=validation_location,
                    message='Computed color {} not BBC-allowed value'
                            .format(c_c),
                    code=ValidationCode.bbc_text_color_constraint
                )

            # For every span, check tts:backgroundColor - ERROR if not a
            # permitted color (black)
            c_bc = el_css.get('backgroundColor').lower()
            # print('backgroundColor = {}'.format(c_bc))

            if c_bc not in permitted_span_backgroundColor_values:
                valid = False
                validation_results.error(
                    location=validation_location,
                    message='Computed backgroundColor {} not BBC-allowed value'
                            .format(c_bc),
                    code=ValidationCode.bbc_text_backgroundColor_constraint
                )

            # For every span, check tts:fontStyle - WARN if "italic"
            c_fs = el_css.get('fontStyle')
            # print('fontStyle = {}'.format(c_fs))
            if c_fs != 'normal':
                validation_results.warn(
                    location=validation_location,
                    message='Computed fontStyle {} not in general use for BBC'
                            .format(c_fs),
                    code=ValidationCode.bbc_text_fontStyle_constraint
                )

        # Recursively call for each child element, passing in el_sss and el_css
        for child_el in el:
            valid &= self._check_styles(
                el=child_el,
                context=context,
                validation_results=validation_results,
                tt_ns=tt_ns,
                parent_css=el_css
            )
        return valid

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        valid = True
        skip = False

        # Gather style references from style, region, body, div, p and span
        # elements in a map from style xml:id to referencing element
        style_to_referencing_els_map = self._gather_style_refs(input=input)

        # Report WARN for all style elements that are not referenced
        if 'id_to_style_map' not in context:
            logging.warning(
                'styleRefsCheck not checking for unreferenced'
                'style elements - no context[id_to_style_map]')
            validation_results.skip(
                location='document',
                message='styleRefsCheck not checking for unreferenced'
                        'style elements - no context[id_to_style_map]',
                code=ValidationCode.ttml_styling
            )
            skip = True
        else:
            for style_id in context['id_to_style_map'].keys():
                if style_id not in style_to_referencing_els_map:
                    validation_results.warn(
                        location='style xml:id={}'.format(style_id),
                        message='Unreferenced style element',
                        code=ValidationCode.ttml_element_style
                    )
            for style_id in style_to_referencing_els_map.keys():
                if style_id not in context['id_to_style_map']:
                    validation_results.warn(
                        location='style xml:id={}'.format(style_id),
                        message='Referenced id does not point '
                                'to a style element',
                        code=ValidationCode.ttml_styling_reference
                    )

            # Compute list of style attributes and values for each
            # referenced style
            id_to_styleattribs_map = {}
            valid &= self._gather_style_attribs(
                id_to_style_map=context['id_to_style_map'],
                validation_results=validation_results,
                id_to_styleattribs_map=id_to_styleattribs_map
            )
            context['id_to_style_attribs_map'] = id_to_styleattribs_map

            tt_ns = \
                context.get('root_ns', ns_ttml)
            body_el_tag = make_qname(tt_ns, 'body')
            bodies = [el for el in input if el.tag == body_el_tag]
            if len(bodies) != 1:
                validation_results.error(
                    location='{}/{}'.format(input.tag, body_el_tag),
                    message='Found {} body elements, expected 1'.format(
                        len(bodies)),
                    code=ValidationCode.ttml_element_body
                )
                valid = False
            else:
                body_el = bodies[0]

                valid &= self._check_styles(
                    el=body_el,
                    context=context,
                    validation_results=validation_results,
                    tt_ns=tt_ns,
                    parent_css={})

        if valid and not skip:
            validation_results.good(
                location='document',
                message='Style references and attributes checked',
                code=ValidationCode.ttml_styling
            )

        return valid
