from .constraintSet import ConstraintSet
from src.preParseChecks.preParseCheck import BadEncodingCheck, NullByteCheck, \
    ByteOrderMarkCheck
from src.preParseChecks.xmlStructureCheck import XmlStructureCheck
from src.schemas.daptSchema import DAPTSchema
from src.xmlChecks.xsdValidator import xsdValidator
from src.xmlChecks.ttXmlCheck import timeBaseCheck, \
    ttTagAndNamespaceCheck, contentProfilesCheck
from src.xmlChecks.xmlIdCheck import unqualifiedIdAttributeCheck, \
    duplicateXmlIdCheck, IDREFSelementApplicabilityCheck
from src.xmlChecks.headXmlCheck import headCheck
from src.xmlChecks.copyrightCheck import copyrightCheck
from src.xmlChecks.actorRefsCheck import actorRefsCheck
from src.xmlChecks.bodyXmlCheck import bodyCheck
from src.xmlChecks.daptmDescTypeCheck import daptmDescTypeCheck
from src.xmlChecks.daptmRepresentsCheck import daptmRepresentsCheck
from src.xmlChecks.daptTimingXmlCheck import daptTimingCheck
from src.xmlChecks.pruner import Pruner
from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationSummariser import \
    XmlPassChecker, TtmlPassChecker, DaptPassChecker

recognised_namespaces = set([
    'http://www.w3.org/XML/1998/namespace',  # xml
    'http://www.w3.org/ns/ttml',  # tt
    'http://www.w3.org/ns/ttml#parameter',  # ttp
    'http://www.w3.org/ns/ttml#audio',  # tta
    'http://www.w3.org/ns/ttml#metadata',  # ttm
    'http://www.w3.org/ns/ttml/feature/',
    'http://www.w3.org/ns/ttml/profile/dapt#metadata',  # daptm
    'http://www.w3.org/ns/ttml/profile/dapt/extension/',
    'urn:ebu:tt:metadata',  # ebuttm
])

# We will not prune attributes in no namespace if they are
# defined on any element in TTML or DAPT, even if they are
# not defined on the specific element on which they occur.
known_no_ns_attributes = set([
    'agent',
    'animate',
    'begin',
    'calcMode',
    'clipBegin',
    'clipEnd',
    'condition',
    'dur',
    'encoding',
    'end',
    'family',
    'fill',
    'format',
    'keySplines',
    'keyTimes',
    'length',
    'name',
    'range',
    'region',
    'repeatCount',
    'src',
    'style',
    'timeContainer',
    'type',
    'weight',
])


class DaptConstraintSet(ConstraintSet):

    _preParseChecks = [
        BadEncodingCheck(),  # check encoding before null bytes
        ByteOrderMarkCheck(),
        NullByteCheck(),
        XmlStructureCheck()
    ]

    _xmlChecks = [
        duplicateXmlIdCheck(),
        Pruner(
            no_prune_namespaces=recognised_namespaces,
            no_prune_no_namespace_attributes=known_no_ns_attributes),
        xsdValidator(xml_schema=DAPTSchema, schema_name='DAPT'),
        unqualifiedIdAttributeCheck(),
        IDREFSelementApplicabilityCheck(),
        ttTagAndNamespaceCheck(),
        timeBaseCheck(
            timeBase_acceptlist=['media'],
            timeBase_required=False),
        contentProfilesCheck(
            contentProfiles_atleastonelist=[
                'http://www.w3.org/ns/ttml/profile/dapt1.0/content',
                ],
            contentProfiles_denylist=[],
            contentProfiles_required=True
        ),
        headCheck(
            sub_checks=[
                copyrightCheck(copyright_required=False),
                actorRefsCheck(),
            ]),
        daptmDescTypeCheck(),
        daptmRepresentsCheck(),
        # bodyCheck(),
    ]  # Note that daptTimingCheck is appended in init method

    def __init__(
            self,
            epoch: float = 0.0,
            segment_dur: float | None = None,
            segment_relative_timing: bool = False) -> None:
        super().__init__()
        self._xmlChecks.append(
            daptTimingCheck(
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

        daptFails, daptWarns, daptSkips = \
            DaptPassChecker.failuresAndWarningsAndSkips(validation_results)
        if daptSkips == 0 and daptFails == 0:
            validation_results.good(
                location='Document',
                message='Document appears to be valid DAPT with {} '
                        'DAPT-related warnings'.format(daptWarns),
                code=ValidationCode.dapt_document_validity
            )
        elif daptSkips == 0:
            validation_results.error(
                location='Document',
                message='Document is not valid DAPT with {} '
                        'DAPT-related failures and '
                        '{} warnings'.format(daptFails, daptWarns),
                code=ValidationCode.dapt_document_validity
            )
        else:
            validation_results.skip(
                location='Document',
                message='{} DAPT checks skipped, '
                        'document {} with '
                        '{} DAPT-related failures and '
                        '{} warnings'.format(
                            daptSkips,
                            'validity as DAPT unclear' if daptFails == 0
                            else 'is not valid DAPT',
                            daptFails,
                            daptWarns),
                code=ValidationCode.ebuttd_document_validity
            )

        totalFails = xmlFails + ttmlFails + daptFails
        totalSkips = xmlSkips + ttmlSkips + daptSkips

        return totalFails, totalSkips
