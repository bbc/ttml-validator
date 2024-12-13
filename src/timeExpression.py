import re

# Framerate multiplier e.g. "1000 1001"
_frm_regex = re.compile(r'(?P<numerator>\d+)\s(?P<denominator>\d+)')

# Clock-time Timecode e.g. "01:00:23:14"
_tc_regex = \
    re.compile(
        r'(?P<h>[0-9][0-9]):(?P<m>[0-5][0-9]):(?P<s>[0-5][0-9]):(?P<f>[0-9][0-9])$')

# hhmmss time e.g. "425000:13:14.040"
_hms_regex = \
    re.compile(
        r'(?P<h>[0-9][0-9]+):(?P<m>[0-5][0-9]):(?P<s>([0-5][0-9])(\.[0-9]+)?)$')

# Offset time e.g. "2016f"
_tm_regex = \
    re.compile(
        r'(?P<count>([0-9]+)(\.[0-9]+)?)(?P<metric>(h)|(m)|(s)|(ms)|(f)|(t))$')


class TimeExpressionHandler:
    _framerate = 25
    _framerate_multiplier = 1.0
    _effective_framerate = 25
    _tickrate = 1

    def _calculateEffectiveFramerate(self):
        return self._framerate * self._framerate_multiplier

    @classmethod
    def _decode_frm(cls, framerate_multiplier: str) -> float:
        m = _frm_regex.match(framerate_multiplier)
        if m is None:
            raise ValueError(
                'Framerate multiplier {} not valid'.format(
                    framerate_multiplier))
        return int(m['numerator'])/int(m['denominator'])

    def __init__(self,
                 framerate: str = None,
                 framerate_multiplier: str = None,
                 tickrate: str = None):
        if framerate is not None:
            self._framerate = int(framerate)
        if framerate_multiplier is not None:
            self._framerate_multiplier = \
                TimeExpressionHandler._decode_frm(framerate_multiplier)
        self._effective_framerate = self._calculateEffectiveFramerate()
        if tickrate is not None:
            if int(tickrate) < 1:
                raise ValueError('tickrate must be positive integer')
            self._tickrate = int(tickrate)
        elif framerate is not None:
            self._tickrate = self._effective_framerate

    def seconds(self, time_value: str) -> float:
        # try hhmmss first
        m = _hms_regex.match(time_value)
        if m is not None:
            # print('Matched {} as mm:hh:ss.sss'.format(time_value))
            seconds = \
                int(m['h']) * 3600 + \
                int(m['m']) * 60 + \
                float(m['s'])
            return seconds

        # try offset time next
        m = _tm_regex.match(time_value)
        if m is not None:
            # print('Matched {} as offset time'.format(time_value))
            count = float(m['count'])
            match m['metric']:
                case 'h':
                    return count * 3600
                case 'm':
                    return count * 60
                case 's':
                    return count
                case 'ms':
                    return count / 1000
                case 'f':
                    return count / self._effective_framerate
                case 't':
                    return count / self._tickrate

        # finally try clock-time timecode
        m = _tc_regex.match(time_value)
        if m is not None:
            # print('Matched {} as mm:hh:ff'.format(time_value))
            if int(m['f']) >= self._framerate:
                raise ValueError(
                    '{} has illegal frame value for frame rate {}'.format(
                        time_value,
                        self._framerate
                    ))
            seconds = \
                int(m['h']) * 3600 + \
                int(m['m']) * 60 + \
                int(m['s']) + \
                float(m['f']) / self._effective_framerate
            return seconds

        raise ValueError(
            '{} is not a recognised time expression'.format(
                time_value))
