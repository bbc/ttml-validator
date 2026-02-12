# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from src.xmlUtils import make_qname, ns_xml
from .ttmlUtils import ns_ttml
from .xmlCheck import XmlCheck


xmllang_attr_tag = make_qname(
    namespace=ns_xml,
    name='lang')


class daptLangAudioNonMatchingCheck(XmlCheck):
    """
    Checks that the computed xml:lang of every <audio> element matches
    its parent's computed xml:lang
    """

    def __init__(self) -> None:
        super().__init__()

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        valid = True

        tt_ns = \
            context.get('root_ns', ns_ttml)
        content_el_tags = [
            make_qname(namespace=tt_ns, name=el_name)
            for el_name in ['body', 'div', 'p', 'span', 'audio']
            ]
        audio_el_tag = make_qname(namespace=tt_ns, name='audio')

        # iterate through the tt/body// to get the computed
        # xml:lang attribute for each <audio> element and its parent
        # and check they match each other.

        valid &= self.recursively_compute_xml_lang_and_check_audio(
            input=input,
            parent_computed_lang='',
            content_el_tags=content_el_tags,
            audio_el_tag=audio_el_tag,
            validation_results=validation_results
        )

        if valid:
            validation_results.good(
                location='audio elements',
                message='xml:lang checked',
                code=ValidationCode.dapt_lang_audio
            )

        return valid

    def recursively_compute_xml_lang_and_check_audio(
            self,
            input: Element,
            parent_computed_lang: str,
            content_el_tags: list[str],
            audio_el_tag: str,
            validation_results: ValidationLogger,
            ) -> bool:
        valid = True

        this_computed_lang = input.get(xmllang_attr_tag, '') \
            if xmllang_attr_tag in input.keys() \
            else parent_computed_lang

        if input.tag == audio_el_tag and \
           this_computed_lang != parent_computed_lang:
            valid = False
            validation_results.error(
                location='audio element xml:lang attribute',
                message='Computed value "{}" is not the same as parent '
                        'element computed value "{}"'
                        .format(this_computed_lang, parent_computed_lang),
                code=ValidationCode.dapt_lang_audio
            )

        children = [el for el in input
                    if el.tag in content_el_tags]
        for child in children:
            valid &= self.recursively_compute_xml_lang_and_check_audio(
                input=child,
                parent_computed_lang=this_computed_lang,
                content_el_tags=content_el_tags,
                audio_el_tag=audio_el_tag,
                validation_results=validation_results
            )

        return valid


class nonEmptyLangRootCheck(XmlCheck):
    """
    Checks xml:lang attribute is present and is not empty
    """

    def __init__(self) -> None:
        super().__init__()

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        valid = True

        if xmllang_attr_tag in input.keys():
            xmllang_attr_val = input.get(xmllang_attr_tag, '')
            if xmllang_attr_val == '':
                valid = False
                validation_results.error(
                    location='{} element'.format(input.tag),
                    message='Empty xml:lang attribute value prohibited',
                    code=ValidationCode.dapt_lang_root
                )
        else:
            valid = False
            validation_results.error(
                location='{} element'.format(input.tag),
                message='Required xml:lang attribute is missing',
                code=ValidationCode.dapt_lang_root
            )

        if valid:
            validation_results.good(
                location='{} element'.format(input.tag),
                message='xml:lang present and not empty',
                code=ValidationCode.dapt_lang_root
            )

        return valid
