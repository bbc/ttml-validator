import unittest
import re
from src.styleAttribs import getAllStyleAttributeKeys, \
    getStyleAttributeKeys, getStyleAttributeDict, \
    StyleAttribute, attributeIsApplicableToElement


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
                 defaultValue=''
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
