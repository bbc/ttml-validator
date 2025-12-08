from .constraintSet import ConstraintSet
from src.preParseChecks.preParseCheck import BadEncodingCheck, NullByteCheck, \
    ByteOrderMarkCheck
from src.preParseChecks.xmlStructureCheck import XmlStructureCheck
from src.schemas.ebuttdSchema import EBUTTDSchema
from src.xmlChecks.xsdValidator import xsdValidator
from src.xmlChecks.ttXmlCheck import timeBaseCheck, \
    ttTagAndNamespaceCheck, activeAreaCheck, cellResolutionCheck
from src.xmlChecks.copyrightCheck import copyrightCheck
from src.xmlChecks.stylingCheck import stylingCheck
from src.xmlChecks.layoutCheck import layoutCheck
from src.xmlChecks.headXmlCheck import headCheck
from src.xmlChecks.styleRefsCheck import styleRefsXmlCheck
from src.xmlChecks.regionRefsCheck import regionRefsXmlCheck
from src.xmlChecks.inlineStyleAttributeCheck import inlineStyleAttributesCheck
from src.xmlChecks.bodyXmlCheck import bodyCheck
from src.xmlChecks.divXmlCheck import divCheck
from src.xmlChecks.pXmlCheck import pCheck
from src.xmlChecks.spanXmlCheck import spanCheck
from src.xmlChecks.bbcTimingXmlCheck import bbcTimingCheck
from src.xmlChecks.xmlIdCheck import requireXmlId, duplicateXmlIdCheck, \
    unqualifiedIdAttributeCheck, IDREFSelementApplicabilityCheck
from src.xmlChecks.timingAttributeCheck import noNestedTimedElementsCheck, \
    noTimingAttributeCheck
from src.xmlChecks.textCheck import noTextChildren, checkLineBreaks
from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationSummariser import \
    XmlPassChecker, TtmlPassChecker, EbuttdPassChecker, \
    BbcPassChecker


class BbcSubtitleConstraintSet(ConstraintSet):
    _preParseChecks = [
        ByteOrderMarkCheck(),  # encoding check will remove BOM
        BadEncodingCheck(),  # check encoding before null bytes
        NullByteCheck(),
        XmlStructureCheck()
    ]

    _xmlChecks = [
        unqualifiedIdAttributeCheck(),
        xsdValidator(xml_schema=EBUTTDSchema, schema_name='EBU-TT-D'),
        duplicateXmlIdCheck(),
        IDREFSelementApplicabilityCheck(),
        ttTagAndNamespaceCheck(),
        timeBaseCheck(timeBase_acceptlist=['media'], timeBase_required=True),
        activeAreaCheck(activeArea_required=False),
        cellResolutionCheck(cellResolution_required=False),
        headCheck(
            sub_checks=[
                copyrightCheck(copyright_required=False),
                stylingCheck(),
                layoutCheck(),
            ]
            ),
        styleRefsXmlCheck(),
        inlineStyleAttributesCheck(),
        regionRefsXmlCheck(),
        bodyCheck(sub_checks=[
            noTimingAttributeCheck(),
            divCheck(sub_checks=[
                noTimingAttributeCheck(),
                pCheck(sub_checks=[
                    requireXmlId(),
                    noTextChildren(),
                    checkLineBreaks(),
                    spanCheck(sub_checks=[
                        noNestedTimedElementsCheck()
                        ],
                        require_text_in_span=True,
                        permit_nested_spans=False)
                    ])
                ],
                recurse_div_children=True)
            ]
        )
    ]

    def __init__(
            self,
            epoch: float = 0.0,
            segment_dur: float | None = None,
            segment_relative_timing: bool = False) -> None:
        super().__init__()
        self._xmlChecks.append(
            bbcTimingCheck(
                epoch=epoch,
                segment_dur=segment_dur,
                segment_relative_timing=segment_relative_timing)
            )

    @staticmethod
    def summarise(validation_results: ValidationLogger) -> tuple[int, int]:
        xmlFails, xmlWarns, xmlSkips = \
            XmlPassChecker.failuresAndWarningsAndSkips(validation_results)
        if xmlSkips == 0 and xmlFails == 0:
            validation_results.good(
                location='Document',
                message='Document appears to be valid XML with {} '
                        'XML-related warnings'.format(xmlWarns),
                code=ValidationCode.xml_document_validity
            )
        elif xmlSkips == 0:
            validation_results.error(
                location='Document',
                message='Document is not valid XML with {} '
                        'XML-related failures and '
                        '{} warnings'.format(xmlFails, xmlWarns),
                code=ValidationCode.xml_document_validity
            )
        else:
            validation_results.skip(
                location='Document',
                message='{} XML checks skipped, '
                        'document {} with '
                        '{} XML-related failures and '
                        '{} warnings'.format(
                            xmlSkips,
                            'validity as XML unclear' if xmlFails == 0 else
                            'is not valid XML',
                            xmlFails,
                            xmlWarns),
                code=ValidationCode.xml_document_validity
            )

        ttmlFails, ttmlWarns, ttmlSkips = \
            TtmlPassChecker.failuresAndWarningsAndSkips(validation_results)
        if ttmlSkips == 0 and ttmlFails == 0:
            validation_results.good(
                location='Document',
                message='Document appears to be valid TTML with {} '
                        'TTML-related warnings'.format(xmlWarns),
                code=ValidationCode.ttml_document_validity
            )
        elif ttmlSkips == 0:
            validation_results.error(
                location='Document',
                message='Document is not valid TTML with {} '
                        'TTML-related failures and '
                        '{} warnings'.format(ttmlFails, ttmlWarns),
                code=ValidationCode.ttml_document_validity
            )
        else:
            validation_results.skip(
                location='Document',
                message='{} TTML checks skipped, '
                        'document {} with '
                        '{} TTML-related failures and '
                        '{} warnings'.format(
                            ttmlSkips,
                            'validity as TTML unclear' if ttmlFails == 0 else
                            'is not valid TTML',
                            ttmlFails,
                            ttmlWarns),
                code=ValidationCode.ttml_document_validity
            )

        ebuttdFails, ebuttdWarns, ebuttdSkips = \
            EbuttdPassChecker.failuresAndWarningsAndSkips(validation_results)
        if ebuttdSkips == 0 and ebuttdFails == 0:
            validation_results.good(
                location='Document',
                message='Document appears to be valid EBU-TT-D with {} '
                        'EBU-TT-D-related warnings'.format(ebuttdWarns),
                code=ValidationCode.ebuttd_document_validity
            )
        elif ebuttdSkips == 0:
            validation_results.error(
                location='Document',
                message='Document is not valid EBU-TT-D with {} '
                        'EBU-TT-D-related failures and '
                        '{} warnings'.format(ebuttdFails, ebuttdWarns),
                code=ValidationCode.ebuttd_document_validity
            )
        else:
            validation_results.skip(
                location='Document',
                message='{} EBU-TT-D checks skipped, '
                        'document {} with '
                        '{} EBU-TT-D-related failures and '
                        '{} warnings'.format(
                            ebuttdSkips,
                            'validity as EBU-TT-D unclear' if ebuttdFails == 0
                            else 'is not valid EBU-TT-D',
                            ebuttdFails,
                            ebuttdWarns),
                code=ValidationCode.ebuttd_document_validity
            )

        mightPlay = (ebuttdFails + ttmlFails + xmlFails == 0)
        bbcFails, bbcWarns, bbcSkips = \
            BbcPassChecker.failuresAndWarningsAndSkips(validation_results)
        if bbcSkips == 0 and bbcFails == 0:
            validation_results.good(
                location='Document',
                message='Document appears to meet BBC requirements '
                        'and should play okay in the BBC\'s player. '
                        'There were {} BBC-related warnings'.format(bbcWarns),
                code=ValidationCode.bbc_document_validity
            )
        elif bbcSkips == 0 and mightPlay:
            validation_results.error(
                location='Document',
                message='Document does not meet BBC '
                        'requirements but may play with unexpected '
                        'appearance in the BBC\'s player. '
                        'There were {} BBC-related errors and '
                        '{} warnings'.format(bbcFails, bbcWarns),
                code=ValidationCode.bbc_document_validity
            )
        elif bbcSkips == 0:
            validation_results.error(
                location='Document',
                message='Document does not meet BBC '
                        'requirements and is likely not to play properly '
                        'if at all in the BBC\'s player. '
                        'There were {} BBC-related errors and '
                        '{} warnings'.format(bbcFails, bbcWarns),
                code=ValidationCode.bbc_document_validity
            )
        else:
            summary_text = \
                'conformance to BBC requirements is unclear with ' \
                if bbcFails == 0 and not mightPlay else \
                'conformance to BBC requirements is unclear but may play ' \
                'with unexpected appearance in the BBC\'s player. ' \
                'There were ' \
                if bbcFails == 0 and mightPlay else \
                'does not meet BBC requirements and is likely not to play ' \
                'properly if at all in the BBC\'s player. There were '
            validation_results.skip(
                location='Document',
                message='{} BBC requirement checks skipped, '
                        'document {} '
                        '{} BBC-related errors and '
                        '{} warnings'.format(
                            bbcSkips,
                            summary_text,
                            bbcFails,
                            bbcWarns),
                code=ValidationCode.bbc_document_validity
            )

        totalFails = xmlFails + ttmlFails + ebuttdFails + bbcFails
        totalSkips = xmlSkips + ttmlSkips + ebuttdSkips + bbcSkips
        return totalFails, totalSkips
