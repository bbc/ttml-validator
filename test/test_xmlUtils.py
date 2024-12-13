import unittest
from src.xmlUtils import get_namespace


class TestNamespaceExtraction(unittest.TestCase):

    def test_well_formed_with_ns(self):
        expected = 'namespace'
        stimulus = '{namespace}name'
        self.assertEqual(expected, get_namespace(stimulus))

    def test_well_formed_with_empty_ns(self):
        expected = ''
        stimulus = '{}name'
        self.assertEqual(expected, get_namespace(stimulus))

    def test_no_ns(self):
        expected = ''
        stimulus = 'name'
        self.assertEqual(expected, get_namespace(stimulus))

    def test_empty(self):
        expected = ''
        stimulus = ''
        self.assertEqual(expected, get_namespace(stimulus))

    def test_no_close_brace(self):
        stimulus = '{whoknowswhatthisissupposedtobe'
        with self.assertRaises(ValueError, msg='No closing brace found'):
            get_namespace(stimulus)
