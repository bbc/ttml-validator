from .validationCodes import ValidationCode
from .validationLogger import ValidationLogger
from .validationResult import ERROR, WARN, SKIP


class ValidationPassChecker():
    _check_codes = []

    @classmethod
    def failuresAndWarningsAndSkips(
            cls,
            log: ValidationLogger) -> tuple[int, int, int]:
        fails = [
            v for v in log
            if v.code in cls._check_codes
            and v.status == ERROR
        ]
        warns = [
            v for v in log
            if v.code in cls._check_codes
            and v.status == WARN
        ]
        skips = [
            v for v in log
            if v.code in cls._check_codes
            and v.status == SKIP
        ]
        return len(fails), len(warns), len(skips)


class XmlPassChecker(ValidationPassChecker):
    _check_codes = [
        ValidationCode.preParse_nullBytes,
        ValidationCode.preParse_encoding,
        ValidationCode.preParse_byteOrderMark,
        ValidationCode.preParse_byteOrderMark_corrupt,
        ValidationCode.xml_parse,
        ValidationCode.xml_id_unique,
        ValidationCode.xml_id_unqualified,
    ]


class TtmlPassChecker(ValidationPassChecker):
    _check_codes = [
        ValidationCode.xml_root_element,
        ValidationCode.xml_tt_namespace,
        ValidationCode.ttml_idref_element_applicability,
        ValidationCode.ttml_idref_empty,
        ValidationCode.ttml_idref_too_many,
        ValidationCode.ttml_parameter_cellResolution,
        ValidationCode.ttml_document_timing,
        ValidationCode.ttml_element_body,
        ValidationCode.ttml_element_br,
        ValidationCode.ttml_element_head,
        ValidationCode.ttml_element_layout,
        ValidationCode.ttml_element_region,
        ValidationCode.ttml_element_style,
        ValidationCode.ttml_element_styling,
        ValidationCode.ttml_metadata_copyright,
        ValidationCode.ttml_layout_region_association,
        ValidationCode.ttml_styling,
        ValidationCode.ttml_styling_reference,
        ValidationCode.ttml_styling_referential_chained,
        ValidationCode.ttml_styling_attribute_applicability,
    ]


class DaptPassChecker(ValidationPassChecker):
    _check_codes = [
        ValidationCode.xml_xsd,
        ValidationCode.xml_encoding_decl,
        ValidationCode.xml_entity_decl,
        ValidationCode.xml_document_validity,
        ValidationCode.xml_prune,  # should never be errors
        ValidationCode.ttml_metadata_actor_reference,
        ValidationCode.ebuttd_parameter_timeBase,
        ValidationCode.ttml_parameter_contentProfiles,
        ValidationCode.dapt_timing_attribute_constraint,
        ValidationCode.dapt_document_validity,
        ValidationCode.dapt_timing_framerate,
        ValidationCode.dapt_timing_origin_timecode,
        ValidationCode.dapt_timing_segment_overlap,
        ValidationCode.dapt_timing_start_of_programme_timecode,
        ValidationCode.dapt_timing_tickrate,
        ValidationCode.dapt_timing_timecode_offset,
        ValidationCode.dapt_timing_timecontainer,
        ValidationCode.ttml_timing_attribute_syntax
    ]


class EbuttdPassChecker(ValidationPassChecker):
    _check_codes = [
        ValidationCode.xml_xsd,
        ValidationCode.ttml_attribute_styling_attribute,
        ValidationCode.ebuttd_parameter_timeBase,
        ValidationCode.ebuttd_p_xml_id_constraint,
        ValidationCode.ebuttd_empty_body_constraint,
        ValidationCode.ebuttd_empty_div_constraint,
        ValidationCode.ebuttd_head_element_constraint,
        ValidationCode.ebuttd_layout_element_constraint,
        ValidationCode.ebuttd_multiRowAlign,
        ValidationCode.ebuttd_nested_div_constraint,
        ValidationCode.ebuttd_nested_span_constraint,
        ValidationCode.ebuttd_nested_timing_constraint,
        ValidationCode.ebuttd_overlapping_region_constraint,
        ValidationCode.ebuttd_region_element_constraint,
        ValidationCode.ebuttd_region_attributes_constraint,
        ValidationCode.ebuttd_region_position_constraint,
        ValidationCode.ebuttd_style_element_constraint,
        ValidationCode.ebuttd_inline_styling_constraint,
        ValidationCode.ebuttd_styling_element_constraint,
        ValidationCode.ebuttd_timing_attribute_constraint,
        ValidationCode.imsc_parameter_activeArea,
    ]


class BbcPassChecker(ValidationPassChecker):
    _check_codes = [
        ValidationCode.bbc_block_backgroundColor_constraint,
        ValidationCode.bbc_region_attributes_constraint,
        ValidationCode.bbc_region_backgroundColor_constraint,
        ValidationCode.bbc_region_overflow_constraint,
        ValidationCode.bbc_region_position_constraint,
        ValidationCode.bbc_text_backgroundColor_constraint,
        ValidationCode.bbc_text_color_constraint,
        ValidationCode.bbc_text_fillLineGap_constraint,
        ValidationCode.bbc_text_fontFamily_constraint,
        ValidationCode.bbc_text_fontSize_constraint,
        ValidationCode.bbc_text_fontStyle_constraint,
        ValidationCode.bbc_text_lineHeight_constraint,
        ValidationCode.bbc_text_linePadding_constraint,
        ValidationCode.bbc_text_multiRowAlign_constraint,
        ValidationCode.bbc_text_span_constraint,
        ValidationCode.bbc_timing_gaps,
        ValidationCode.bbc_timing_minimum_subtitles,
        ValidationCode.bbc_timing_segment_overlap,
    ]
