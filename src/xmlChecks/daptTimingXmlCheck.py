from typing import Tuple
from ..validationLogging.validationCodes import ValidationCode
from ..validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from ..xmlUtils import get_unqualified_name, make_qname, \
    xmlIdAttr
from .xmlCheck import XmlCheck
from ..timeExpression import TimeExpressionHandler
import traceback


timing_attr_keys = [
    'begin',
    'end',
    'dur',
    'clipBegin',
    'clipEnd',
]


class daptTimingCheck(XmlCheck):
    """
    Checks timings in document

    Things we need to check:

    * Time expressions are well formed in begin, end, dur, clipBegin
        and clipEnd attributes:
    * clock-time hh:mm:ss or hh:mm:ss.sss
    * offset-time nn metric or nn.nn metric where metric is h, m, s, ms, f or t
    * Time expressions are well formed in
        /tt/head/metadata/daptm:daptOriginTimecode and
        /tt/head/metadata/ebuttm:documentStartOfProgramme:
    * clock-time hh:mm:ss:ff for either
    * offset-time a permitted alternative for documentStartOfProgramme
    * If both daptOriginTimecode and documentStartOfProgramme are present,
        but they are different, warn that the contents may be offset by delta
        relative to the related media
    * If f units are used, there's a ttp:frameRate on tt
    * frameRate: non-negative integer
    * If t units are used, there's a ttp:tickRate on tt
    * tickRate: non-negative integer
    * If timeContainer is present, its value is "par"
    * error if a different value
    * warn if present and "par"

    Extra things to check:
    * What's the earliest begin and latest end time, for info
    * In case this is in a segment, do the times overlap the segment interval?
    """

    def __init__(self,
                 epoch: float = 0.0,
                 segment_dur: float | None = None,
                 segment_relative_timing: bool = False):
        super().__init__()
        self._epoch = epoch
        self._segment_dur = segment_dur
        self._segment_relative_timing = segment_relative_timing

    def _check_for_timeContainer(
            self,
            el: Element,
            validation_results: ValidationLogger
            ) -> bool:
        valid = True

        if 'timeContainer' in el.keys():
            tcv = el.get('timeContainer', '')
            if tcv != 'par':
                valid = False
                validation_results.error(
                    location='{} element xml:id {}'.format(
                        el.tag,
                        el.get(xmlIdAttr, 'omitted')),
                    message='timeContainer {} prohibited'
                            .format(tcv),
                    code=ValidationCode.dapt_timing_timecontainer
                )
            else:
                validation_results.warn(
                    location='{} element xml:id {}'.format(
                        el.tag,
                        el.get(xmlIdAttr, 'omitted')),
                    message='timeContainer present but should be omitted',
                    code=ValidationCode.dapt_timing_timecontainer
                )

        return valid

    def _safe_get_timing_attr_seconds(
            self,
            te: TimeExpressionHandler,
            el: Element,
            attr_key: str,
            default: float | None,
            validation_results: ValidationLogger
            ) -> Tuple[float | None, bool]:
        valid = True
        rv = default
        # print('getting seconds for '+attr_key)
        if attr_key in el.keys():
            value, in_valid = self._safe_get_timing_seconds_from_str(
                te=te,
                val=el.get(attr_key, ''),
                validation_results=validation_results,
                location='{} element xml:id {}, {} attribute'
                         .format(
                            el.tag,
                            el.get(xmlIdAttr, 'omitted'),
                            attr_key)
            )
            valid = in_valid
            if valid:
                rv = value

        return rv, valid

    def _safe_get_timing_seconds_from_str(
            self,
            te: TimeExpressionHandler,
            val: str,
            validation_results: ValidationLogger,
            location: str
            ) -> Tuple[float | None, bool]:
        valid = True
        rv = None

        try:
            rv = te.seconds(val)
        except ValueError as ve:
            valid = False
            validation_results.error(
                location=location,
                message=str(ve),
                code=ValidationCode.ttml_timing_attribute_syntax
            )

        return rv, valid

    def _collect_timed_elements(
            self,
            te: TimeExpressionHandler,
            el: Element,
            epoch_s: float,
            parent_end: float | None,
            begin_defined: bool,
            end_defined: bool,
            time_el_map: dict[float, list[tuple[Element, float]]],
            validation_results: ValidationLogger,
            # depth: int = 0
            ) -> tuple[bool, float, float]:
        # prefix = '  ' * depth
        # print('{}_collect_timed_elements for {}, epoch: {}s, begin_defined: {}'.
        #       format(prefix, el.tag, epoch_s, begin_defined))
        valid = True

        for timing_attr in timing_attr_keys:
            if timing_attr in el.keys():
                time_val = el.get(timing_attr, "")
                if not te.isOffsetTime(time_expression=time_val) \
                   and not te.isNonFrameClockTime(time_expression=time_val):
                    valid = False
                    validation_results.error(
                        location='{} element xml:id {}'.format(
                            el.tag,
                            el.get(xmlIdAttr, 'omitted')),
                        message='{}={} is not a valid time expression'.format(
                            timing_attr,
                            el.get(timing_attr)),
                        code=ValidationCode.dapt_timing_attribute_constraint
                    )
                if not self._frameRateSpecified \
                   and te.usesFrames(time_expression=time_val):
                    valid = False
                    validation_results.error(
                        location='{} element xml:id {}'.format(
                            el.tag,
                            el.get(xmlIdAttr, 'omitted')),
                        message='{} attribute {} uses frames but '
                                'frame rate not specified on tt element'
                                .format(timing_attr, time_val),
                        code=ValidationCode.dapt_timing_framerate
                    )
                if not self._tickRateSpecified \
                   and te.usesTicks(time_expression=time_val):
                    valid = False
                    validation_results.error(
                        location='{} element xml:id {}'.format(
                            el.tag,
                            el.get(xmlIdAttr, 'omitted')),
                        message='{} attribute {} uses ticks but '
                                'tick rate not specified on tt element'
                                .format(timing_attr, time_val),
                        code=ValidationCode.dapt_timing_tickrate
                    )

        valid &= self._check_for_timeContainer(
            el=el,
            validation_results=validation_results)

        this_begin, begin_valid = self._safe_get_timing_attr_seconds(
            te=te, el=el, attr_key='begin',
            default=0,
            validation_results=validation_results)
        valid &= begin_valid
        if 'begin' in el.keys():
            begin_defined = True
            # print('{}begin is defined by this element'.format(prefix))
        this_epoch_s = epoch_s + this_begin

        this_end, end_valid = self._safe_get_timing_attr_seconds(
            te=te, el=el, attr_key='end',
            default=parent_end,
            validation_results=validation_results)
        valid &= end_valid
        if 'end' in el.keys():
            end_defined = True
            if parent_end is not None and this_end is not None:
                this_end = min(parent_end, this_end)
        this_dur, dur_valid = self._safe_get_timing_attr_seconds(
            te=te, el=el, attr_key='dur',
            default=None,
            validation_results=validation_results)
        valid &= dur_valid
        if 'dur' in el.keys() and this_dur is not None:
            end_defined = True
            dur_end = this_epoch_s + this_dur
            if this_end is not None:
                this_end = min(this_end, dur_end)
            else:
                this_end = dur_end

        child_begins = []
        child_ends = []
        timed_elements = ['div', 'p', 'span', 'audio']
        for child_el in el:
            # br and metadata elements cannot have begin attributes
            if get_unqualified_name(child_el.tag) in timed_elements:
                (child_valid, child_begin, child_end) = \
                    self._collect_timed_elements(
                        te=te,
                        el=child_el,
                        epoch_s=this_epoch_s,
                        parent_end=this_end,
                        begin_defined=begin_defined,
                        end_defined=end_defined,
                        time_el_map=time_el_map,
                        validation_results=validation_results,
                        # depth=depth + 1
                        )
                valid &= child_valid
                child_begins.append(child_begin)
                child_ends.append(child_end)

        child_begins.sort()
        if not begin_defined and len(child_begins) > 0:
            # print(prefix+'setting epoch for {} to {}'.format(el.tag, child_begins[0]))
            this_epoch_s = child_begins[0]
        # elif begin_defined:
        #     print(prefix+'for {}, begin is defined, not setting epoch'.format(el.tag))
        # else:
        #     print(prefix+'for {}, begin not defined but no child begins'.format(el.tag))

        if not end_defined and len(child_ends) > 0:
            this_end = child_ends[-1]

        el_list = time_el_map.get(this_epoch_s, [])
        el_list.append((el, this_end))
        time_el_map[this_epoch_s] = el_list

        return (valid, this_epoch_s, this_end)

    def _makeTimeExpressionHandler(
            self,
            tt: Element,
            tt_ns: str,
            ) -> TimeExpressionHandler:
        ttp_ns = tt_ns + '#parameter'
        preferredFrameRateKey = make_qname(ttp_ns, 'frameRate')
        frameRateKey = preferredFrameRateKey \
            if preferredFrameRateKey in tt.keys() \
            else 'frameRate'
        preferredFrameRateMultiplierKey = \
            make_qname(ttp_ns, 'frameRateMultiplier')
        frameRateMultiplierKey = preferredFrameRateMultiplierKey \
            if preferredFrameRateMultiplierKey in tt.keys() \
            else 'frameRateMultiplier'
        preferredTickRateKey = make_qname(ttp_ns, 'tickRate')
        tickRateKey = preferredTickRateKey \
            if preferredTickRateKey in tt.keys() \
            else 'tickRate'

        self._frameRateSpecified = frameRateKey in tt.keys()
        self._tickRateSpecified = tickRateKey in tt.keys()

        return TimeExpressionHandler(
            framerate=tt.get(frameRateKey),
            framerate_multiplier=tt.get(frameRateMultiplierKey),
            tickrate=tt.get(tickRateKey)
        )

    def _checkTimedContentOverlapsSegment(
            self,
            doc_begin: float,
            doc_end: float,
            validation_results: ValidationLogger) -> bool:
        valid = True

        if self._segment_dur is not None:
            epoch = 0 if self._segment_relative_timing else self._epoch
            max_end = epoch + self._segment_dur

            if doc_begin > max_end or \
               (doc_end is not None and doc_end <= epoch):
                valid = False
                validation_results.error(
                    location='Timed content',
                    message='Document content is timed outside the segment '
                            'interval [{}s..{}s)'.format(epoch, max_end),
                    code=ValidationCode.dapt_timing_segment_overlap
                )
            else:
                validation_results.good(
                    location='Timed content',
                    message='Document content overlaps the segment '
                            'interval [{}s..{}s)'.format(epoch, max_end),
                    code=ValidationCode.dapt_timing_segment_overlap
                )

        return valid

    @classmethod
    def _dot_dsop_paths(cls, tt_ns: str) -> tuple[str, str]:
        metadata_path = './{}/{}'.format(
            make_qname(namespace=tt_ns, name='head'),
            make_qname(namespace=tt_ns, name='metadata')
        )
        dot_path = '{}/{}'.format(
            metadata_path,
            make_qname(
                namespace='http://www.w3.org/ns/ttml/profile/dapt#metadata',
                name='daptOriginTimecode')
        )
        dsop_path = '{}/{}'.format(
            metadata_path,
            make_qname(
                namespace='urn:ebu:tt:metadata',
                name='documentStartOfProgramme'
            )
        )
        return (dot_path, dsop_path)

    def _checkOriginAndStartOfProgramme(
            self,
            tt: Element,
            tt_ns: str,
            te: TimeExpressionHandler,
            validation_results: ValidationLogger) -> bool:
        """
        * Time expressions are well formed in
            /tt/head/metadata/daptm:daptOriginTimecode and
            /tt/head/metadata/ebuttm:documentStartOfProgramme:
        * clock-time hh:mm:ss:ff permissible in either
        * offset-time a permitted alternative for documentStartOfProgramme
        * If both daptOriginTimecode and documentStartOfProgramme are present,
            but they are different, warn that the contents may be offset by
            delta relative to the related media
        """
        valid = True

        dot_path, dsop_path = daptTimingCheck._dot_dsop_paths(tt_ns=tt_ns)
        dots = tt.findall(dot_path)
        dsops = tt.findall(dsop_path)
        dot = None
        dsop = None
        if len(dots) > 1:
            valid = False
            validation_results.error(
                location=dot_path,
                message='Expected max 1 daptOriginTimecode, found {}'
                        .format(len(dots)),
                code=ValidationCode.dapt_timing_origin_timecode
            )
        if len(dsops) > 1:
            valid = False
            validation_results.error(
                location=dsop_path,
                message='Expected max 1 documentStartOfProgramme, found {}'
                        .format(len(dsops)),
                code=ValidationCode.dapt_timing_origin_timecode
            )
        if len(dots) == 1:
            dot = dots[0].text if dots[0].text else ''
            if not te.isFrameClockTime(time_expression=dot):
                valid = False
                validation_results.error(
                    location=dot_path,
                    message='daptOriginTimecode value "{}" is '
                            'not a valid format'
                            .format(dot),
                    code=ValidationCode.dapt_timing_origin_timecode
                )
            else:
                if not self._frameRateSpecified:
                    valid = False
                    validation_results.error(
                        location=dsop_path,
                        message='daptOriginTimecode uses frames '
                                'but frame rate not specified on tt element.',
                        code=ValidationCode.dapt_timing_framerate
                    )
        if len(dsops) == 1:
            dsop = dsops[0].text if dsops[0].text else ''
            if not te.isFrameClockTime(time_expression=dsop) \
               and not te.isOffsetTime(time_expression=dsop):
                valid = False
                validation_results.error(
                    location=dsop_path,
                    message='documentStartOfProgramme value "{}" is '
                            'not a valid format'
                            .format(dsop),
                    code=ValidationCode.dapt_timing_start_of_programme_timecode
                )
            else:
                if te.usesFrames(time_expression=dsop) \
                   and not self._frameRateSpecified:
                    valid = False
                    validation_results.error(
                        location=dsop_path,
                        message='documentStartOfProgramme uses frames '
                                'but frame rate not specified on tt element.',
                        code=ValidationCode.dapt_timing_framerate
                    )
                if te.usesTicks(time_expression=dsop) \
                   and not self._tickRateSpecified:
                    valid = False
                    validation_results.error(
                        location=dsop_path,
                        message='documentStartOfProgramme uses ticks '
                                'but tick rate not specified on tt element.',
                        code=ValidationCode.dapt_timing_tickrate
                    )

        (dot_secs, dot_valid) = self._safe_get_timing_seconds_from_str(
            te=te, val=dot, validation_results=validation_results,
            location=dot_path) \
            if dot \
            else (None, True)
        (dsop_secs, dsop_valid) = self._safe_get_timing_seconds_from_str(
            te=te, val=dsop, validation_results=validation_results,
            location=dsop_path) \
            if dsop \
            else (None, True)
        if not dot_valid or not dsop_valid:
            valid = False
        elif dot_secs is not None and dsop_secs is not None:
            delta = dot_secs - dsop_secs
            if delta != 0:
                validation_results.warn(
                    location='Timecode-related metadata',
                    message='Non-zero delta between daptOriginTimecode {} '
                            'and documentStartOfProgramme {} suggests '
                            'document times may need to be offset by {:.3f}s'
                            .format(dot, dsop, delta),
                    code=ValidationCode.dapt_timing_timecode_offset
                )

        return valid

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        tt_ns = \
            context.get('root_ns', 'http://www.w3.org/ns/ttml')

        valid = True

        time_expression_handler = self._makeTimeExpressionHandler(
            tt=input,
            tt_ns=tt_ns
        )

        valid &= self._checkOriginAndStartOfProgramme(
            tt=input,
            tt_ns=tt_ns,
            te=time_expression_handler,
            validation_results=validation_results
        )

        time_el_map = {}
        body_el_key = make_qname(namespace=tt_ns, name='body')
        body_el = input.find('./'+body_el_key)
        if body_el is None:
            body_el = input.find('./{*}body')
        if body_el is None:
            validation_results.skip(
                location='{} element'.format(input.tag),
                message='No body element found, skipping timing tests',
                code=ValidationCode.ttml_document_timing
            )
            return valid

        try:
            (te_valid, doc_begin, doc_end) = self._collect_timed_elements(
                te=time_expression_handler,
                el=body_el,
                epoch_s=0,
                parent_end=None,
                begin_defined=False,
                end_defined=False,
                time_el_map=time_el_map,
                validation_results=validation_results)
            valid &= te_valid

            valid &= self._checkTimedContentOverlapsSegment(
                doc_begin=doc_begin,
                doc_end=doc_end,
                validation_results=validation_results
            )

            validation_results.info(
                location='Document',
                message='First text appears at {}s, end of doc is {}'.format(
                    doc_begin,
                    'undefined' if doc_end is None else '{}s'.format(doc_end)
                ),
                code=ValidationCode.ttml_document_timing
            )
        except Exception as e:
            valid = False
            validation_results.error(
                location='body element or descendants',
                message='Exception encountered while trying to compute times:'
                        ' {}, trace: {}'
                        .format(
                            str(e),
                            ''.join(traceback.format_exception(e))),
                code=ValidationCode.ttml_document_timing
            )

        return valid
