# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationResult import ValidationResult, \
    ERROR, WARN
from src.validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from src.xmlUtils import make_qname
from .xmlCheck import XmlCheck
from .ttmlUtils import ns_ttml


class copyrightCheck(XmlCheck):
    """
    Checks presence of copyright element in head
    """

    def __init__(self,
                 copyright_required: bool = False) -> None:
        super().__init__()
        self._copyright_required = copyright_required

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        tt_ns = \
            context.get('root_ns', ns_ttml)
        ttm_ns = tt_ns + '#metadata'
        copyright_el_tag = make_qname(ttm_ns, 'copyright')
        copyright_els = [el for el in input if el.tag == copyright_el_tag]
        valid = True
        if len(copyright_els) == 0:
            valid = not self._copyright_required
            validation_results.append(ValidationResult(
                status=ERROR if self._copyright_required else WARN,
                location='{}/{}'.format(input.tag, copyright_el_tag),
                message='{}copyright element absent'.format(
                        'Required ' if self._copyright_required else ''),
                code=ValidationCode.ttml_metadata_copyright
            ))
        elif len(copyright_els) > 1:
            validation_results.warn(
                location='{}/{}'.format(input.tag, copyright_el_tag),
                message='{} copyright elements found, expected 1'.format(
                    len(copyright_els)),
                code=ValidationCode.ttml_metadata_copyright
            )
        else:  # 1 copyright element
            validation_results.good(
                location='{}/{}'.format(input.tag, copyright_el_tag),
                message='Copyright element found',
                code=ValidationCode.ttml_metadata_copyright
            )
        return valid
