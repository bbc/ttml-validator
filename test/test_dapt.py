# from _typeshed import ReadableBuffer
from typing import Any
from unittest import TestCase
from argparse import Namespace
import io
import json
import os
import sys
from src.ttmlValidator import validate_ttml


dapt_tests_path = os.path.join(
    os.path.dirname(__file__), 'dapt-tests/dapt1/validation')
dapt_tests_json_path = os.path.normpath(
    os.path.join(
        dapt_tests_path,
        'tests.json')
    )
dapt_valid_path = os.path.normpath(
    os.path.join(
        dapt_tests_path,
        'valid')
    )
dapt_invalid_path = os.path.normpath(
    os.path.join(
        dapt_tests_path,
        'invalid')
    )
dapt_extension = '.xml'


class namedTestBuffer(io.BytesIO):
    name = 'namedTestBuffer'

    def __init__(self, initial_bytes: Any = b"") -> None:
        super().__init__(initial_bytes)
        self.name = self.__class__.name


class testDAPT(TestCase):
    """
    Tests that this validator correctly validates the files in the DAPT test
    suite at https://www.github.com/w3c/dapt-tests which is brought in to
    this repo as a git submodule.
    """

    maxDiff = None

    _dapt_tests = {}

    def _loadTestJson(self):
        with open(dapt_tests_json_path, 'r') as f:
            self._dapt_tests = json.load(fp=f)

    def _runTest(self, path: str):
        result = None
        with open(path, 'rb') as test_file:
            results_out = io.TextIOWrapper(
                buffer=namedTestBuffer(), encoding='utf-8', newline='\n')
            args = Namespace(
                ttml_in=test_file,
                results_out=results_out,
                # results_out=sys.stdout,
                csv=False,
                json=False,
                segment=False,
                segdur='3.84',
                segment_relative_timing=False,
                vertical=False,
                collate_more_than=5,
                flavour='dapt',
            )
            result = validate_ttml(args)
            results_out.flush()
            results_out.seek(0)
            results_text = results_out.read()
        return result, results_text

    def setUp(self) -> None:
        self._loadTestJson()
        return super().setUp()

    def test_valid_dapt_tests(self):
        for feature, all_tests in self._dapt_tests.items():
            for valid_tests in all_tests.get('valid', []):
                test_name = valid_tests.get('test')
                test_path = os.path.normpath(os.path.join(
                    dapt_valid_path,
                    test_name + dapt_extension
                ))
                with self.subTest(
                        feature=feature,
                        name=test_name,
                        path=test_path):
                    result, results_text = self._runTest(path=test_path)
                    if result != 0:
                        print(results_text)
                    self.assertEqual(result, 0)

    def test_invalid_dapt_tests(self):
        for feature, all_tests in self._dapt_tests.items():
            for invalid_tests in all_tests.get('invalid', []):
                test_name = invalid_tests.get('test')
                test_path = os.path.normpath(os.path.join(
                    dapt_invalid_path,
                    test_name + dapt_extension
                ))
                with self.subTest(
                        feature=feature,
                        name=test_name,
                        path=test_path):
                    result, results_text = self._runTest(path=test_path)
                    if result == 0:
                        print(results_text)
                    self.assertGreater(result, 0)
