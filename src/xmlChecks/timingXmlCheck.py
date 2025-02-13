from math import floor
from ..validationResult import ValidationResult, ERROR, GOOD, WARN, INFO
from xml.etree.ElementTree import Element
from ..xmlUtils import get_unqualified_name, make_qname, \
    xmlIdAttr
from .xmlCheck import xmlCheck
from ..timeExpression import TimeExpressionHandler
from operator import itemgetter
import traceback

timing_attr_keys = [
    'begin',
    'end',
    'dur'
]


class timingCheck(xmlCheck):
    """
    Checks timings in document
    """

    _min_short_gap = 0.8
    _desired_min_gap = 1.5
    _min_count_early_begins = 2
    _early_begin_threshold = 23 * 60  # First 23 minutes

    def __init__(self,
                 epoch: float = 0.0,
                 segment_dur: float | None = None,
                 segment_relative_timing: bool = False):
        super().__init__()
        self._epoch = epoch
        self._segment_dur = segment_dur
        self._segment_relative_timing = segment_relative_timing

    def _collect_timed_elements(
            self,
            te: TimeExpressionHandler,
            el: Element,
            epoch_s: float,
            parent_end: float,
            begin_defined: bool,
            end_defined: bool,
            time_el_map: dict[float, list[tuple[Element, float]]],
            validation_results: list[ValidationResult],
            # depth: int = 0
            ) -> tuple[bool, float, float]:
        # prefix = '  ' * depth
        # print('{}_collect_timed_elements for {}, epoch: {}s, begin_defined: {}'.
        #       format(prefix, el.tag, epoch_s, begin_defined))
        valid = True

        for timing_attr in timing_attr_keys:
            if timing_attr in el.keys():
                if not te.isOffsetTime(el.get(timing_attr)):
                    valid = False
                    validation_results.append(ValidationResult(
                        status=ERROR,
                        location='{} element xml:id {}'.format(
                            el.tag,
                            el.get(xmlIdAttr, 'omitted')),
                        message='{}={} is not a valid offset time'.format(
                            timing_attr,
                            el.get(timing_attr))
                    ))

        this_begin = te.seconds(el.get('begin')) \
            if 'begin' in el.keys() \
            else 0
        if 'begin' in el.keys():
            begin_defined = True
            # print('{}begin is defined by this element'.format(prefix))
        this_epoch_s = epoch_s + this_begin
        this_end = epoch_s + te.seconds(el.get('end')) \
            if 'end' in el.keys() \
            else parent_end
        if 'end' in el.keys():
            end_defined = True
            if parent_end is not None and this_end is not None:
                this_end = min(parent_end, this_end)
        # TODO: Handle dur attribute if present

        child_begins = []
        child_ends = []
        for child_el in el:
            # br and metadata elements cannot have begin attributes
            if get_unqualified_name(child_el.tag) in ['div', 'p', 'span']:
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

        return TimeExpressionHandler(
            framerate=tt.get(frameRateKey),
            framerate_multiplier=tt.get(frameRateMultiplierKey),
            tickrate=tt.get(tickRateKey)
        )

    def _checkEnoughSubsAtBeginning(
            self,
            time_el_map: dict[float, list[tuple[Element, float]]],
            validation_results: list[ValidationResult],
            ) -> bool:
        valid = True

        count_early_begins = 0

        early_begin_threshold = self._early_begin_threshold + self._epoch
        for begin, el_list in time_el_map.items():
            if begin >= early_begin_threshold:
                continue

            count_early_begins += len(
                [el[1] for el in el_list
                 if get_unqualified_name(el[0].tag) in ['p']])

        if count_early_begins < self._min_count_early_begins:
            valid = False
            hours = floor(early_begin_threshold / 3600)
            minutes = floor((early_begin_threshold - hours * 3600) / 60)
            seconds = early_begin_threshold % 60
            validation_results.append(ValidationResult(
                status=ERROR,
                location='p elements beginning before {:02}:{:02}:{:06.3f}'
                         .format(
                             hours,
                             minutes,
                             seconds),
                message='{} subtitle(s) found, minimum {} required'
                        .format(
                            count_early_begins,
                            self._min_count_early_begins)
            ))

        return valid

    def _checkForShortGaps(
            self,
            time_el_map: dict[float, list[tuple[Element, float]]],
            validation_results: list[ValidationResult],
            ) -> bool:
        valid = True

        begin_end_list = []
        for begin, el_list in time_el_map.items():
            end_list = [el[1] for el in el_list 
                        if get_unqualified_name(el[0].tag) in ['span', 'p']]
            max_end = max(end_list) if None not in end_list else None
            begin_end_list.append((begin, max_end))
        begin_end_list.sort(key=itemgetter(0))

        for i in range(0, len(begin_end_list) - 1):
            gap_to_next = begin_end_list[i+1][0] - begin_end_list[i][1]

            if gap_to_next > 0 and gap_to_next < self._min_short_gap:
                valid = False
                validation_results.append(ValidationResult(
                    status=ERROR,
                    location='Gap from {}s to {}s'.format(
                        begin_end_list[i][1],
                        begin_end_list[i+1][0]
                    ),
                    message='Non-zero gap between subtitles is '
                            'shorter than {}s'
                            .format(self._min_short_gap)
                ))
            elif gap_to_next >= self._min_short_gap \
                    and gap_to_next < self._desired_min_gap:
                validation_results.append(ValidationResult(
                    status=WARN,
                    location='Gap from {}s to {}s'.format(
                        begin_end_list[i][1],
                        begin_end_list[i+1][0]
                    ),
                    message='Short gap between subtitles should be '
                            'at least {}s'
                            .format(self._desired_min_gap)
                ))

        return valid

    def _checkSubsOverlapSegment(
            self,
            doc_begin: float,
            doc_end: float,
            validation_results: list[ValidationResult]) -> bool:
        valid = True

        if self._segment_dur is not None:
            epoch = 0 if self._segment_relative_timing else self._epoch
            max_end = epoch + self._segment_dur

            if doc_begin > max_end or \
               (doc_end is not None and doc_end <= epoch):
                valid = False
                validation_results.append(ValidationResult(
                    status=ERROR,
                    location='Timed content',
                    message='Document content is timed outside the segment '
                            'interval [{}s..{}s)'.format(epoch, max_end)
                ))
            else:
                validation_results.append(ValidationResult(
                    status=GOOD,
                    location='Timed content',
                    message='Document content overlaps the segment '
                            'interval [{}s..{}s)'.format(epoch, max_end)
                ))

        return valid

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: list[ValidationResult]) -> bool:
        tt_ns = \
            context.get('root_ns', 'http://www.w3.org/ns/ttml')

        valid = True

        time_expression_handler = self._makeTimeExpressionHandler(
            tt=input,
            tt_ns=tt_ns
        )

        time_el_map = {}
        body_el_key = make_qname(namespace=tt_ns, name='body')
        body_el = input.find('./'+body_el_key)
        if body_el is None:
            body_el = input.find('./{*}body')
        if body_el is None:
            validation_results.append(ValidationResult(
                status=WARN,
                location='{} element'.format(input.tag),
                message='No body element found, skipping timing tests'
            ))
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

            valid &= self._checkForShortGaps(
                time_el_map=time_el_map,
                validation_results=validation_results
            )

            if self._segment_dur is None \
               or self._early_begin_threshold <= self._segment_dur:
                valid &= self._checkEnoughSubsAtBeginning(
                    time_el_map=time_el_map,
                    validation_results=validation_results
                )
            else:
                validation_results.append(ValidationResult(
                    status=INFO,
                    location='Document',
                    message='Skipping check for enough early subtitles '
                            'because segment duration is shorter than '
                            'search period.'
                ))
                valid &= self._checkSubsOverlapSegment(
                    doc_begin=doc_begin,
                    doc_end=doc_end,
                    validation_results=validation_results
                )

            validation_results.append(ValidationResult(
                status=INFO,
                location='Document',
                message='First text appears at {}s, end of doc is {}'.format(
                    doc_begin,
                    'undefined' if doc_end is None else '{}s'.format(doc_end)
                )
            ))
        except Exception as e:
            valid = False
            validation_results.append(ValidationResult(
                status=ERROR,
                location='body element or descendants',
                message='Exception encountered while trying to compute times:'
                        ' {}, trace: {}'
                        .format(str(e), ''.join(traceback.format_exception(e)))
            ))

        return valid
