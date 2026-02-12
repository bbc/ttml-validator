# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

import unittest
import re
from src.styleAttribs import getAllStyleAttributeKeys, \
    getStyleAttributeKeys, getStyleAttributeDict, \
    StyleAttribute, attributeIsApplicableToElement, \
    getAllStyleAttributeDict, _getCellHeight, \
    _getPercentRelativeSize, _computeUninheritedAttribute, \
    _fallbackToDefault


class testStyleAttribs(unittest.TestCase):
    maxDiff = None

    def test_getAllStyleAttributeKeys(self):
        actual = getAllStyleAttributeKeys(tt_ns='ttml:ns:prefix')
        expected = [
            '{ttml:ns:prefix#styling}direction',
            '{ttml:ns:prefix#styling}fontFamily',
            '{ttml:ns:prefix#styling}fontSize',
            '{ttml:ns:prefix#styling}lineHeight',
            '{ttml:ns:prefix#styling}textAlign',
            '{ttml:ns:prefix#styling}color',
            '{ttml:ns:prefix#styling}backgroundColor',
            '{ttml:ns:prefix#styling}fontStyle',
            '{ttml:ns:prefix#styling}fontWeight',
            '{ttml:ns:prefix#styling}textDecoration',
            '{ttml:ns:prefix#styling}unicodeBidi',
            '{ttml:ns:prefix#styling}wrapOption',
            '{urn:ebu:tt:style}multiRowAlign',
            '{urn:ebu:tt:style}linePadding',
            '{http://www.w3.org/ns/ttml/profile/imsc1#styling}fillLineGap',
            '{ttml:ns:prefix#styling}origin',
            '{ttml:ns:prefix#styling}extent',
            '{ttml:ns:prefix#styling}displayAlign',
            '{ttml:ns:prefix#styling}padding',
            '{ttml:ns:prefix#styling}writingMode',
            '{ttml:ns:prefix#styling}showBackground',
            '{ttml:ns:prefix#styling}overflow',
            'style',
        ]
        self.assertListEqual(actual, expected)

    def test_getStyleAttributeKeys_span(self):
        actual = getStyleAttributeKeys(
            tt_ns='ttml:ns:prefix',
            elements=['span']
        )
        expected = [
            '{ttml:ns:prefix#styling}direction',
            '{ttml:ns:prefix#styling}fontFamily',
            '{ttml:ns:prefix#styling}fontSize',
            '{ttml:ns:prefix#styling}color',
            '{ttml:ns:prefix#styling}backgroundColor',
            '{ttml:ns:prefix#styling}fontStyle',
            '{ttml:ns:prefix#styling}fontWeight',
            '{ttml:ns:prefix#styling}textDecoration',
            '{ttml:ns:prefix#styling}unicodeBidi',
            '{ttml:ns:prefix#styling}wrapOption',
            'style',
        ]
        self.assertListEqual(actual, expected)

    def test_getStyleAttributeKeys_region(self):
        actual = getStyleAttributeKeys(
            tt_ns='ttml:ns:prefix',
            elements=['region']
        )
        expected = [
            '{ttml:ns:prefix#styling}backgroundColor',
            '{ttml:ns:prefix#styling}origin',
            '{ttml:ns:prefix#styling}extent',
            '{ttml:ns:prefix#styling}displayAlign',
            '{ttml:ns:prefix#styling}padding',
            '{ttml:ns:prefix#styling}writingMode',
            '{ttml:ns:prefix#styling}showBackground',
            '{ttml:ns:prefix#styling}overflow',
            'style',
        ]
        self.assertListEqual(actual, expected)

    def test_getStyleAttributeKeys_p_span(self):
        actual = getStyleAttributeKeys(
            tt_ns='ttml:ns:prefix',
            elements=['p', 'span']
        )
        expected = [
            '{ttml:ns:prefix#styling}direction',
            '{ttml:ns:prefix#styling}fontFamily',
            '{ttml:ns:prefix#styling}fontSize',
            '{ttml:ns:prefix#styling}lineHeight',
            '{ttml:ns:prefix#styling}textAlign',
            '{ttml:ns:prefix#styling}color',
            '{ttml:ns:prefix#styling}backgroundColor',
            '{ttml:ns:prefix#styling}fontStyle',
            '{ttml:ns:prefix#styling}fontWeight',
            '{ttml:ns:prefix#styling}textDecoration',
            '{ttml:ns:prefix#styling}unicodeBidi',
            '{ttml:ns:prefix#styling}wrapOption',
            '{urn:ebu:tt:style}multiRowAlign',
            '{urn:ebu:tt:style}linePadding',
            '{http://www.w3.org/ns/ttml/profile/imsc1#styling}fillLineGap',
            'style',
        ]
        self.assertListEqual(actual, expected)

    def test_getStyleAttributeDict_style(self):
        actual = getStyleAttributeDict(
            tt_ns='ttml:ns:prefix', elements=['style'])
        expected = {
            'style':
            StyleAttribute(
                 ns='',
                 nsIsRelative=False,
                 tag='style',
                 appliesTo=['style', 'region', 'body', 'div', 'p', 'span'],
                 syntaxRegex=re.compile(
                     r'^([a-zA-Z_][\S]*([\t\f ]+([a-zA-Z_][\S]*))*)?$'),
                 defaultValue='',
                 computeValue=_computeUninheritedAttribute,
                 fallbackComputeValue=_fallbackToDefault
            )
            }
        self.assertDictEqual(actual, expected)

    def test_attributeIsApplicableToElement(self):
        is_applicable = [
            ('color', 'span'),
            ('backgroundColor', 'span'),
            ('backgroundColor', 'region'),
            ('fillLineGap', 'p')
        ]
        is_not_applicable = [
            ('color', 'p'),
            ('textAlign', 'span'),
            ('lineHeight', 'div'),
            ('fillLineGap', 'region')
        ]

        for (attr_key, el_tag) in is_applicable:
            with self.subTest(attr_key=attr_key, el_tag=el_tag):
                self.assertTrue(attributeIsApplicableToElement(
                    attr_key=attr_key,
                    el_tag=el_tag
                ))

        for (attr_key, el_tag) in is_not_applicable:
            with self.subTest(attr_key=attr_key, el_tag=el_tag):
                self.assertFalse(attributeIsApplicableToElement(
                    attr_key=attr_key,
                    el_tag=el_tag
                ))

    def test_computeFontSize(self):
        font_style_attr = \
            getAllStyleAttributeDict(tt_ns='')['{#styling}fontSize']
        specified = '150%'
        parent = '100%'
        params = {'{ttml#parameters}cellResolution': '32 16'}
        computed = font_style_attr.computeValue(specified, parent, params)
        self.assertEqual(computed[-1:], '%')
        self.assertAlmostEqual(float(computed[:-1]), 150, 5)

        parent = ''
        computed = font_style_attr.computeValue(specified, parent, params)
        self.assertEqual(computed[-2:], 'rh')
        self.assertAlmostEqual(float(computed[:-2]), 9.375, 5)

        params = {}
        computed = font_style_attr.computeValue(specified, parent, params)
        self.assertEqual(computed[-2:], 'rh')
        self.assertAlmostEqual(float(computed[:-2]), 10, 5)

        specified = '1c'
        with self.assertRaises(ValueError) as ve:
            computed = font_style_attr.computeValue(specified, parent, params)
        self.assertEqual(
            str(ve.exception),
            '1c is not a valid fontSize'
            )

    def test_computeLineHeight(self):
        line_height_attr = \
            getAllStyleAttributeDict(tt_ns='')['{#styling}lineHeight']
        specified = 'normal'
        parent = 'normal'
        params = {'fontSize': '7.5rh'}
        computed = line_height_attr.computeValue(
            specified=specified,
            parent=parent,
            params=params
        )
        self.assertEqual(computed, 'normal')

        specified = '120%'
        computed = line_height_attr.computeValue(
            specified=specified,
            parent=parent,
            params=params
        )
        self.assertEqual(computed[-2:], 'rh')
        self.assertAlmostEqual(float(computed[:-2]), 9, 5)

        parent = '7.500000rh'
        computed = line_height_attr.computeValue(
            specified=specified,
            parent=parent,
            params=params
        )
        self.assertEqual(computed[-2:], 'rh')
        self.assertAlmostEqual(float(computed[:-2]), 9, 5)

        specified = ''
        computed = line_height_attr.computeValue(
            specified=specified,
            parent=parent,
            params=params
        )
        self.assertEqual(computed[-2:], 'rh')
        self.assertAlmostEqual(float(computed[:-2]), 7.5, 5)

    def test_getCellHeight(self):
        params = {
            '{ttml#parameters}cellResolution': '32 16'
        }
        result = _getCellHeight(params)
        self.assertEqual(result, '6.250000rh')

        # default of 1/15 should apply
        params = {}
        result = _getCellHeight(params)
        self.assertEqual(result, '6.666667rh')

        # too many params should raise exception
        params = {
            '{ttml#parameters}cellResolution': '32 16',
            '{bogus}cellResolution': 'who cares'
        }
        with self.assertRaises(ValueError) as ve:
            result = _getCellHeight(params)

        self.assertEqual(
            str(ve.exception),
            "Too many cellResolution parameters in "
            "{'{ttml#parameters}cellResolution': '32 16', "
            "'{bogus}cellResolution': 'who cares'}"
        )

    def test_getPercentRelativeSize(self):
        # Unitless
        self.assertEqual(
            _getPercentRelativeSize('100%', '100'), '100.000000'
        )
        # Percent of percent
        self.assertEqual(
            _getPercentRelativeSize('80%', '80%'), '64.000000%'
        )
        # Random units
        self.assertEqual(
            _getPercentRelativeSize('120%', '0.01freds'), '0.012000freds'
        )

        # Invalid percent
        with self.assertRaises(ValueError) as ve:
            _getPercentRelativeSize('10', 'nan')
        self.assertEqual(
            str(ve.exception),
            'Specified value 10 is not a valid percentage value')

        # Invalid basis
        with self.assertRaises(ValueError) as ve:
            _getPercentRelativeSize('10%', 'nan')
        self.assertEqual(
            str(ve.exception),
            'Basis value nan is not a valid number')

    def test_validateValue_ok(self):
        good_values = [
            ('{#styling}direction', 'rtl'),
            ('{#styling}fontFamily', 'some string, another string, default'),
            ('{#styling}fontSize', '12.45%'),
            ('{#styling}lineHeight', 'normal'),
            ('{#styling}lineHeight', '99.99%'),
            ('{#styling}textAlign', 'start'),
            ('{#styling}color', '#12abcd'),
            ('{#styling}color', '#34abcdef'),
            ('{#styling}backgroundColor', '#12abcd'),
            ('{#styling}backgroundColor', '#34abcdef'),
            ('{#styling}fontStyle', 'italic'),
            ('{#styling}fontWeight', 'normal'),
            ('{#styling}textDecoration', 'none'),
            ('{#styling}unicodeBidi', 'bidiOverride'),
            ('{#styling}wrapOption', 'noWrap'),
            ('{urn:ebu:tt:style}multiRowAlign', 'center'),
            ('{urn:ebu:tt:style}linePadding', '0.5c'),
            ('{http://www.w3.org/ns/ttml/profile/imsc1#styling}fillLineGap', 'true'),
            ('{#styling}origin', '10% 20.5%'),
            ('{#styling}extent', '50.123% 30%'),
            ('{#styling}padding', '1%'),
            ('{#styling}padding', '1% 2.5%'),
            ('{#styling}padding', '1.5% 2.5% 3%'),
            ('{#styling}padding', '1.5% 2.5% 3% 5%'),
            ('{#styling}writingMode', 'tblr'),
            ('{#styling}showBackground', 'whenActive'),
            ('{#styling}overflow', 'visible'),
            ('style', 's1 style_other')
        ]

        allStyleDict = getAllStyleAttributeDict(tt_ns='')

        for (style_attr_key, value) in good_values:
            with self.subTest(
                    style_attr_key=style_attr_key,
                    value=value):
                style_attr = allStyleDict.get(style_attr_key)
                self.assertTrue(style_attr.validateValue(value=value))

    def test_validateValue_bad(self):
        good_values = [
            ('{#styling}direction', 'forward'),
            ('{#styling}fontFamily', '"badly quoted'),
            ('{#styling}fontSize', '1'),
            ('{#styling}fontSize', '3.5em'),
            ('{#styling}lineHeight', '2c'),
            ('{#styling}textAlign', 'weekend'),
            ('{#styling}color', '#12abcg'),
            ('{#styling}color', 'blueish'),
            ('{#styling}backgroundColor', '#12abcg'),
            ('{#styling}backgroundColor', 'blueish'),
            ('{#styling}fontStyle', 'florid'),
            ('{#styling}fontWeight', '3kg'),
            ('{#styling}textDecoration', '3'),
            ('{#styling}unicodeBidi', 'involuted'),
            ('{#styling}wrapOption', 'golden'),
            ('{urn:ebu:tt:style}multiRowAlign', 'arctic'),
            ('{urn:ebu:tt:style}linePadding', '0.5%'),
            ('{http://www.w3.org/ns/ttml/profile/imsc1#styling}fillLineGap', 'possible'),
            ('{#styling}origin', '110% 20.5%'),
            ('{#styling}extent', '-50.123% 30%'),
            ('{#styling}padding', '1% '),
            ('{#styling}padding', '1% 2.5px'),
            ('{#styling}padding', '1.5% 2.5c 3px'),
            ('{#styling}padding', 'quilt 1.5% 2.5% 3% 5%'),
            ('{#styling}writingMode', 'random'),
            ('{#styling}showBackground', 'curious'),
            ('{#styling}overflow', 'niagara'),
            ('style', 's1 1style_other')
        ]

        allStyleDict = getAllStyleAttributeDict(tt_ns='')

        for (style_attr_key, value) in good_values:
            with self.subTest(
                    style_attr_key=style_attr_key,
                    value=value):
                style_attr = allStyleDict.get(style_attr_key)
                self.assertFalse(style_attr.validateValue(value=value))
