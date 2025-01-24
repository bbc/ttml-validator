from typing import Dict, List
from ..validationResult import ValidationResult, ERROR, GOOD, WARN
from xml.etree.ElementTree import Element
from ..xmlUtils import make_qname, xmlIdAttr, get_unqualified_name
from .xmlCheck import xmlCheck
from ..styleAttribs import getStyleAttributeKeys, \
    getAllStyleAttributeDict, attributeIsApplicableToElement
import logging


class styleRefsXmlCheck(xmlCheck):
    """
    Checks for unreferenced styles and inappropriate style attributes.
    """

    def _gather_style_refs(
            self,
            input: Element,
    ) -> Dict[str, List[Element]]:
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
            id_to_style_map: Dict[str, Element],
            style_attrib_map: Dict[str, str],
            visited_styles: List[str],
            validation_results: List[ValidationResult],
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
            id_to_style_map: Dict[str, Element],
            validation_results: List[ValidationResult],
            id_to_styleattribs_map: Dict[str, Dict[str, str]],
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
            element_tags: List[str],
            id_to_styleattribs_map: Dict[str, Dict[str, str]],
            id_to_referencing_els_map: Dict[str, List[Element]],
            validation_results: List[ValidationResult]
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

    def run(
            self,
            input: Element,
            context: Dict,
            validation_results: List[ValidationResult]) -> bool:
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

            # For all references from span elements, check that the referenced
            # attributes apply to span, and ERROR for any that do not.
            valid &= self._check_attr_applicability(
                element_tags=['span'],
                id_to_styleattribs_map=id_to_styleattribs_map,
                id_to_referencing_els_map=style_to_referencing_els_map,
                validation_results=validation_results)

        # For all references from elements other than span, check that there
        # is no non-transparent tts:backgroundColor attribute (BBC requirement)
        # - if there is, ERROR

        # Check for referenced style lists that have wrong computed
        # tts:fontFamily value (BBC requirement) - if there is, ERROR

        # Compute fontSize for every p and span,
        # and check it is within BBC range 2% - 8%
        # ERROR if not

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

        if valid:
            validation_results.append(
                ValidationResult(
                    status=GOOD,
                    location='document',
                    message='Style references and attributes checked'
                )
            )
        return valid
