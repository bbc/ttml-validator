from ..validationResult import ValidationResult, ERROR, GOOD, WARN
from xml.etree.ElementTree import Element
from ..xmlUtils import make_qname, xmlIdAttr, get_unqualified_name, get_namespace
from .xmlCheck import xmlCheck
from ..styleAttribs import getAllStyleAttributeKeys, \
    getAllStyleAttributeDict, attributeIsApplicableToElement
import logging


class styleRefsXmlCheck(xmlCheck):
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
            validation_results: list[ValidationResult],
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
                validation_results.append(
                    ValidationResult(
                        status=ERROR,
                        location='style element',
                        message='Cyclic style ref to {} found'.format(
                            style_ref)
                    ))
                valid = False

        for key, value in style_el.items():
            if key != 'style':
                style_attrib_map[key] = value

        return valid

    def _gather_style_attribs(
            self,
            id_to_style_map: dict[str, Element],
            validation_results: list[ValidationResult],
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
            validation_results: list[ValidationResult]
            ) -> bool:
        valid = True

        for attr_key in sss.keys():
            if not attributeIsApplicableToElement(
                    attr_key=get_unqualified_name(
                        attr_key), el_tag=tag):
                valid = False
                validation_results.append(
                    ValidationResult(
                        status=ERROR,
                        location='{} element'.format(tag),
                        message='Specified style attribute {} is not '
                                'applicable to element type {}'
                                .format(attr_key, tag)
                    ))

        return valid

    def _check_attr_applicability_old(
            self,
            element_tags: list[str],
            id_to_styleattribs_map: dict[str, dict[str, str]],
            id_to_referencing_els_map: dict[str, list[Element]],
            validation_results: list[ValidationResult]
            ) -> bool:
        valid = True

        for style_id, referencing_els in id_to_referencing_els_map.items():
            attrib_dict = id_to_styleattribs_map.get(style_id, {})
            el_tags = set(get_unqualified_name(el.tag)
                          for el in referencing_els
                          if get_unqualified_name(el.tag) in element_tags)
            for el_tag in el_tags:
                for attr_key in attrib_dict.keys():
                    if not attributeIsApplicableToElement(
                            attr_key=get_unqualified_name(
                                attr_key), el_tag=el_tag):
                        valid = False
                        validation_results.append(
                            ValidationResult(
                                status=ERROR,
                                location='{} element referencing style id {}'
                                         .format(el_tag, style_id),
                                message='Specified style attribute {} is not '
                                        'applicable to element type'
                                        .format(attr_key)
                            ))
        return valid

    def _get_merged_style_attribs(
            self,
            el: Element,
            id_to_styleattribs_map: dict[str, dict[str, str]],
    ) -> dict[str, str]:

        style_attr_val = el.get('style', '')
        ref_style_ids = style_attr_val.split()
        style_set = {}
        # Merge referential and chained referential styles
        for ref_style_id in ref_style_ids:
            attrib_dict = id_to_styleattribs_map.get(ref_style_id, {})
            for key, value in attrib_dict.items():
                if key != 'style':
                    style_set[key] = value
        # Merge inline styles (even though there shouldn't be any)
        tt_ns = get_namespace(el.tag)
        style_attr_keys = getAllStyleAttributeKeys(tt_ns=tt_ns)
        for key in style_attr_keys:
            if key != 'style' and key in el.keys():
                style_set[key] = el.get(key)

        return style_set

    def _check_no_backgroundColor(
            self,
            sss: dict[str, str],
            el_tag: str,
            tt_ns: str,
            validation_results: list[ValidationResult]
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
                    validation_results.append(
                        ValidationResult(
                            status=ERROR,
                            location='{} element {} attribute'
                                     .format(el_tag, style_attr_key),
                            message='backgroundColor attribute {} '
                                    'is not valid'
                                    .format(backgroundColor_val)
                        ))
                else:
                    a = int(parsed_bg.group('a'), 16) \
                        if parsed_bg.group('a') else 255
                    if a != 0:
                        valid = False
                        validation_results.append(
                            ValidationResult(
                                status=ERROR,
                                location='{} element {} attribute'
                                         .format(
                                            el_tag,
                                            style_attr_key),
                                message='backgroundColor {} is not '
                                        'transparent (BBC requirement)'
                                        .format(backgroundColor_val)
                            ))

        return valid

    def _check_styles(
                    self,
                    el: Element,
                    context: dict,
                    validation_results: list[ValidationResult],
                    tt_ns: str,
                    parent_sss: dict,
                    parent_css: dict) -> bool:
        valid = True

        id_to_styleattribs_map = context['id_to_style_attribs_map']

        # Iterate through the elements from body down to span
        # For each, gather the specified style set
        # and compute the computed styles, then pass the
        # computed style set down to each child to compute
        # its style set.
        el_sss = self._get_merged_style_attribs(
            el=el,
            id_to_styleattribs_map=id_to_styleattribs_map
        )

        el_tag = get_unqualified_name(el.tag)

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

        # Check for referenced style lists that have wrong computed
        # tts:fontFamily value (BBC requirement) - if there is, ERROR

        # Compute fontSize for every p and span,
        # and check it is within BBC range 2% - 8%
        # ERROR if not
        el_css = {}

        # Compute lineHeight for every p, ERROR if <100% or >130%,
        # WARN if "normal"

        # For every p, check if ebutts:multiRowAlign is present (INFO) and
        # if not auto and different from tts:textAlign, WARN (BBC requirement)

        # For every p, check ebutts:linePadding - ERROR if absent,
        # ERROR if out of range

        # For every span, check tts:color - ERROR if not a permitted color

        # For every span, check tts:backgroundColor - ERROR if not a
        # permitted color (black)

        # For every p, check itts:fillLineGap - ERROR if not true

        # For every span, check tts:fontStyle - WARN if "italic"

        # Recursively call for each child element, passing in el_sss and el_css
        for child_el in el:
            valid &= self._check_styles(
                el=child_el,
                context=context,
                validation_results=validation_results,
                tt_ns=tt_ns,
                parent_sss=el_sss,
                parent_css=el_css
            )
        return valid

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: list[ValidationResult]) -> bool:
        valid = True

        # Gather style references from style, region, body, div, p and span
        # elements in a map from style xml:id to referencing element
        style_to_referencing_els_map = self._gather_style_refs(input=input)

        # Report WARN for all style elements that are not referenced
        if 'id_to_style_map' not in context:
            logging.warning(
                'styleRefsCheck not checking for unreferenced'
                'style elements - no context[id_to_style_map]')
        else:
            for style_id in context['id_to_style_map'].keys():
                if style_id not in style_to_referencing_els_map:
                    validation_results.append(ValidationResult(
                        status=WARN,
                        location='style xml:id={}'.format(style_id),
                        message='Unreferenced style element'
                    ))
            for style_id in style_to_referencing_els_map.keys():
                if style_id not in context['id_to_style_map']:
                    validation_results.append(ValidationResult(
                        status=WARN,
                        location='style xml:id={}'.format(style_id),
                        message='Referenced id does not point '
                                'to a style element'
                    ))

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
                context.get('root_ns', 'http://www.w3.org/ns/ttml')
            body_el_tag = make_qname(tt_ns, 'body')
            bodies = [el for el in input if el.tag == body_el_tag]
            if len(bodies) != 1:
                validation_results.append(ValidationResult(
                    status=ERROR,
                    location='{}/{}'.format(input.tag, body_el_tag),
                    message='Found {} body elements, expected 1'.format(
                        len(bodies))
                ))
                valid = False
            else:
                body_el = bodies[0]

                valid &= self._check_styles(
                    el=body_el,
                    context=context,
                    validation_results=validation_results,
                    tt_ns=tt_ns,
                    parent_sss={},
                    parent_css={})

        if valid:
            validation_results.append(
                ValidationResult(
                    status=GOOD,
                    location='document',
                    message='Style references and attributes checked'
                )
            )
        return valid
