from ..validationLogging.validationResult import ValidationResult, ERROR, GOOD, WARN
from xml.etree.ElementTree import Element
from ..xmlUtils import make_qname, get_unqualified_name
from .xmlCheck import xmlCheck
from ..styleAttribs import computeStyles, getMergedStyleSet, \
    ebutt_distribution_color_type_regex, two_percent_vals_regex
import logging


required_region_style_attrib_keys = [
    'origin',
    'extent',
    'displayAlign',
    'overflow',
]


class regionRefsXmlCheck(xmlCheck):
    """
    Checks for unreferenced regions and inappropriate style attributes
    on region elements.
    """

    def _gather_region_refs(
            self,
            input: Element,
            parent_region_ref: str,
            valid_refs: dict[str, list[Element]],
            dropped_refs: dict[str, list[Element]],
            no_region_ps: list[Element],
    ) -> None:

        # Inner function for adding a reference to a list
        def add_ref(
                el: Element,
                region_ref: str,
                ref_map: dict[str, list[Element]]
        ) -> None:
            referencing_el_list = ref_map.get(region_ref, [])
            referencing_el_list.append(el)
            ref_map[region_ref] = referencing_el_list

            return

        # Get all region references by recursing down the tree
        # logging dropped references for elements that specify
        # a region that differs from the region specified by an
        # ancestor element.
        region_attr_key = 'region'
        region_ref = ''
        if region_attr_key in input.keys():
            region_ref = input.get(region_attr_key)
            if parent_region_ref \
               and region_ref \
               and parent_region_ref != region_ref:
                add_ref(el=input, region_ref=region_ref, ref_map=dropped_refs)
            elif region_ref:
                add_ref(el=input, region_ref=region_ref, ref_map=valid_refs)

        if get_unqualified_name(input.tag) == 'p' \
           and not region_ref and not parent_region_ref:
            no_region_ps.append(input)

        if not region_ref:
            region_ref = parent_region_ref

        # Recurse through the tree
        for el in input:
            self._gather_region_refs(
                input=el,
                parent_region_ref=region_ref,
                valid_refs=valid_refs,
                dropped_refs=dropped_refs,
                no_region_ps=no_region_ps,
            )

        return

    def checkSpecifiedStyles(
            self,
            tt_ns: str,
            sss: dict[str, str],
            validation_results: list[ValidationResult],
            location: str,
            error_significance: int = ERROR,
            ) -> bool:
        valid = True

        ns_qualified_required_region_style_attribs = \
            [make_qname(tt_ns + '#styling', k)
             for k in required_region_style_attrib_keys]
        for attr_key in ns_qualified_required_region_style_attribs:
            if attr_key not in sss:
                if error_significance == ERROR:
                    valid = False
                validation_results.append(ValidationResult(
                    status=error_significance,
                    location=location,
                    message='Required style attribute {} '
                            'missing from region element'
                            .format(attr_key)
                ))

        for sss_key in sss:
            if sss_key not in ns_qualified_required_region_style_attribs:
                validation_results.append(ValidationResult(
                    status=WARN,
                    location=location,
                    message='Non-required style attribute {} '
                            'present on region element - '
                            'presentation may differ from expectation'
                            .format(sss_key)
                ))

        return valid

    def checkComputedStyles(
            self,
            css: dict[str, str],
            validation_results: list[ValidationResult],
            location: str,
            error_significance: int = ERROR,
            ) -> bool:
        valid = True
        error_validity = False if error_significance == ERROR else True

        # Iterate through the computed styles that
        # apply to region checking value is ok

        # backgroundColor
        c_bgc = css.get('backgroundColor', '[invalid value]')
        c_bgc_match = ebutt_distribution_color_type_regex.match(c_bgc)
        c_bgc_alpha = c_bgc_match.group('a') if c_bgc_match else None
        if not c_bgc_alpha or c_bgc_alpha != '00':
            valid = error_validity
            validation_results.append(ValidationResult(
                status=error_significance,
                location=location,
                message='backgroundColor value {} is non-transparent '
                        'and does not meet BBC requirements'
                        .format(c_bgc)
            ))

        # origin and extent must not make a region that goes outside the
        # rendering area. The regex prevents negative values.
        c_origin = css.get('origin', '[invalid value]')
        c_origin_match = two_percent_vals_regex.match(c_origin)
        c_extent = css.get('extent', '[invalid value]')
        c_extent_match = two_percent_vals_regex.match(c_extent)
        if not c_origin_match or not c_extent_match:
            valid = error_validity
            validation_results.append(ValidationResult(
                status=error_significance,
                location=location,
                message='Not got computed values for both origin and extent'
            ))
        else:
            left_edge = float(c_origin_match.group('x'))
            right_edge = \
                left_edge \
                + float(c_extent_match.group('x'))
            top_edge = float(c_origin_match.group('y'))
            bottom_edge = \
                top_edge \
                + float(c_extent_match.group('y'))
            if round(right_edge, 3) > 100.0:
                valid = error_validity
                validation_results.append(ValidationResult(
                    status=error_significance,
                    location=location,
                    message='Region right edge {}% '
                            'goes beyond 100%'
                            .format(right_edge)
                ))
            if round(bottom_edge, 3) > 100.0:
                valid = error_validity
                validation_results.append(ValidationResult(
                    status=error_significance,
                    location=location,
                    message='Region bottom edge {}% '
                            'goes beyond 100%'
                            .format(bottom_edge)
                ))

            # Also check for BBC-defined limits
            if round(left_edge) < 5.0 \
               or round(right_edge) > 95.0 \
               or round(top_edge) < 5.0 \
               or round(bottom_edge) > 95.0:
                valid = error_validity
                validation_results.append(ValidationResult(
                    status=error_significance,
                    location=location,
                    message='Region extends out of BBC-defined '
                            'permitted area (90% height and width)'
                ))

        # displayAlign - BBC requirement to be in specified set,
        # so if we've got this far then it must be valid already

        # padding - BBC says nothing about this, EBU-TT-D permits it;
        # any valid value is ok

        # writingMode - any valid value is ok

        # showBackground - any valid value is ok
        # (but the backgroundColor has to be transparent anyway!)

        # overflow - BBC requirement to set to visible
        c_overflow = css.get('overflow', '[invalid value]')
        if c_overflow != 'visible':
            valid = error_validity
            validation_results.append(ValidationResult(
                status=error_significance,
                location=location,
                message='Region overflow {} '
                        'not visible (BBC requirement)'
                        .format(c_overflow)
            ))

        return valid

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: list[ValidationResult]) -> bool:
        valid = True

        # Gather region references from body, div, p and span
        # elements in a map from region xml:id to referencing element
        tt_ns = \
            context.get('root_ns', 'http://www.w3.org/ns/ttml')
        body_el_tag = make_qname(tt_ns, 'body')
        bodies = [el for el in input if el.tag == body_el_tag]
        if len(bodies) != 1:
            validation_results.append(ValidationResult(
                status=ERROR,
                location='{}/{}'.format(input.tag, body_el_tag),
                message='Found {} body elements, expected 1; '
                        'skipping region reference checks'
                        .format(
                            len(bodies))
            ))
            valid = False
        else:
            body_el = bodies[0]

            valid_refs = {}
            dropped_refs = {}
            no_region_ps = []
            self._gather_region_refs(
                input=body_el,
                parent_region_ref='',
                valid_refs=valid_refs,
                dropped_refs=dropped_refs,
                no_region_ps=no_region_ps)

            # Report WARN for all region elements that are not referenced
            if 'id_to_region_map' not in context:
                logging.warning(
                    'regionRefsCheck not checking for unreferenced'
                    'region elements - no context[id_to_region_map]')
            else:
                for region_id in context['id_to_region_map'].keys():
                    style_error_significance = ERROR
                    if region_id not in dropped_refs \
                       and region_id not in valid_refs:
                        validation_results.append(ValidationResult(
                            status=WARN,
                            location='region element xml:id {}'
                                     .format(region_id),
                            message='Unreferenced region element'
                        ))
                    if region_id in dropped_refs:
                        validation_results.append(ValidationResult(
                            status=WARN,
                            location='region element xml:id {}'
                                     .format(region_id),
                            message='{} elements pruned because their '
                                    'ancestor references a different '
                                    'region element'
                                    .format(len(dropped_refs[region_id]))
                        ))
                    if region_id not in valid_refs:
                        style_error_significance = WARN

                    # Validate the style attributes on this region
                    # and WARN on problems if it is unreferenced,
                    # otherwise ERROR
                    region_el = context['id_to_region_map'][region_id]
                    if 'id_to_style_attribs_map' not in context:
                        logging.warning(
                            'regionRefsCheck not checking region style'
                            'attributes - no context[id_to_style_attribs_map]')
                    else:
                        id_to_styleattribs_map = \
                            context['id_to_style_attribs_map']
                        region_sss = getMergedStyleSet(
                            region_el,
                            id_to_styleattribs_map=id_to_styleattribs_map)
                        location = 'region element xml:id {}'.format(region_id)
                        valid &= self.checkSpecifiedStyles(
                            tt_ns=tt_ns,
                            sss=region_sss,
                            validation_results=validation_results,
                            location=location,
                            error_significance=style_error_significance
                        )
                        region_css = {}
                        params = {}
                        valid &= computeStyles(
                            tt_ns=tt_ns,
                            validation_results=validation_results,
                            el_sss=region_sss,
                            el_css=region_css,
                            parent_css={},
                            params=params,
                            error_significance=style_error_significance
                        )
                        # Also check the region specific computed styles are in
                        # range
                        valid &= self.checkComputedStyles(
                            css=region_css,
                            validation_results=validation_results,
                            location=location,
                            error_significance=style_error_significance)

                # Check for region references that
                # don't point to region elements
                for region_id in valid_refs.keys():
                    if region_id not in context['id_to_region_map']:
                        valid = False
                        validation_results.append(ValidationResult(
                            status=ERROR,
                            location='{} element(s)'
                                     .format(len(valid_refs[region_id])),
                            message='Referenced region {} does not point '
                                    'to a region element'
                                    .format(region_id)
                        ))
                for region_id in dropped_refs.keys():
                    if region_id not in context['id_to_region_map']:
                        valid = False
                        validation_results.append(ValidationResult(
                            status=ERROR,
                            location='{} element(s)'
                                     .format(len(dropped_refs[region_id])),
                            message='Dropped referenced region {} does not '
                                    'point to a region element'
                                    .format(region_id)
                        ))

            # Report ERROR for any p elements not associated with a region
            if len(no_region_ps) > 0:
                valid = False
                validation_results.append(ValidationResult(
                    status=ERROR,
                    location='{} p element(s)'.format(len(no_region_ps)),
                    message='Elements not associated with a region'
                ))

        if valid:
            validation_results.append(
                ValidationResult(
                    status=GOOD,
                    location='document',
                    message='Region references and attributes checked'
                )
            )
        return valid
