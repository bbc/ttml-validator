import unittest
from src.timeExpression import TimeExpressionHandler


class TestTimeExpressionHandlers(unittest.TestCase):
    def testInstantiateTimeExpressionHandler(self):
        TimeExpressionHandler()
        TimeExpressionHandler(framerate="50")
        TimeExpressionHandler(framerate="30", framerate_multiplier="1000 1001")
        TimeExpressionHandler(framerate="25", tickrate="50")

        with self.assertRaises(
                ValueError,
                msg='Framerate multiplier 100 not valid'):
            TimeExpressionHandler(framerate="24", framerate_multiplier="100")

        with self.assertRaises(
                ValueError,
                msg='tickrate must be positive integer'):
            TimeExpressionHandler(tickrate="0")

    def testHHMMSS(self):
        tm = TimeExpressionHandler()
        time_expression = '01:23:45.01'
        seconds = tm.seconds(time_expression)
        self.assertTrue(
            tm.isNonFrameClockTime(time_expression=time_expression))
        self.assertFalse(
            tm.isFrameClockTime(time_expression=time_expression))
        self.assertFalse(
            tm.isOffsetTime(time_expression=time_expression))
        self.assertFalse(
            tm.usesFrames(time_expression=time_expression))
        self.assertFalse(
            tm.usesTicks(time_expression=time_expression))
        self.assertAlmostEqual(seconds, 5025.01, 3)

    def testOffsetTime(self):
        tm = TimeExpressionHandler(tickrate='20')
        tvs = [
            ['1.5h', 5400],
            ['1.5m', 90],
            ['1234.56s', 1234.56],
            ['40ms', 0.04],
            ['125f', 5],
            ['99t', 4.95]
        ]
        for tv in tvs:
            with self.subTest(time_expression=tv[0], expected=tv[1]):
                self.assertTrue(tm.isOffsetTime(time_expression=tv[0]))
                self.assertFalse(tm.isFrameClockTime(
                    time_expression=tv[0]))
                self.assertFalse(tm.isNonFrameClockTime(
                    time_expression=tv[0]))
                self.assertAlmostEqual(tm.seconds(tv[0]), tv[1], 3)

    def testOffsetTimeWithFrames(self):
        tm = TimeExpressionHandler()
        time_expression = '10f'
        self.assertTrue(tm.usesFrames(time_expression=time_expression))

    def testOffsetTimeWithTicks(self):
        tm = TimeExpressionHandler()
        time_expression = '10t'
        self.assertTrue(tm.usesTicks(time_expression=time_expression))

    def testFrameClockTimecode(self):
        tm = TimeExpressionHandler()
        time_expression = '01:23:45:01'
        seconds = tm.seconds(time_expression)
        self.assertTrue(tm.isFrameClockTime(time_expression=time_expression))
        self.assertFalse(
            tm.isNonFrameClockTime(time_expression=time_expression))
        self.assertFalse(tm.isOffsetTime(time_expression=time_expression))
        self.assertTrue(tm.usesFrames(time_expression=time_expression))
        self.assertFalse(tm.usesTicks(time_expression=time_expression))
        self.assertAlmostEqual(seconds, 5025.04, 3)
