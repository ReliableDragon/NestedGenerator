import unittest
import logging

import choices_parser

logging.basicConfig(level=logging.DEBUG)

class PartSplitterTestCase(unittest.TestCase):

    def test_empty_elements(self):
        elements = ''
        self.assertEqual(choices_parser.split_into_parts(elements), [])

    def test_single_elements(self):
        elements = 'abc'
        self.assertEqual(choices_parser.split_into_parts(elements), ['abc'])

    def test_simple_elements(self):
        elements = 'abc def ghi'
        self.assertEqual(choices_parser.split_into_parts(elements), ['abc', 'def', 'ghi'])

    def test_quoted_elements(self):
        elements = 'abc def "*([ghi jkl])*" mno'
        expected = ['abc', 'def', '"*([ghi jkl])*"', 'mno']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_starting_quoted_elements(self):
        elements = '"abc def" ghi jkl mno'
        expected = ['"abc def"', 'ghi', 'jkl', 'mno']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_ending_quoted_elements(self):
        elements = 'abc def ghi "jkl mno"'
        expected = ['abc', 'def', 'ghi', '"jkl mno"']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_parenthetized_elements(self):
        elements = 'abc def (ghi jkl) mno'
        expected = ['abc', 'def', ['ghi', 'jkl'], 'mno']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_single_parenthetized_element(self):
        elements = '(abc)'
        expected = [['abc']]
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_single_multipart_parenthetized_element(self):
        elements = '(abc def)'
        expected = [['abc', 'def']]
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_single_nested_parenthetized_element(self):
        elements = '(((abc)))'
        expected = [[[['abc']]]]
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_single_nested_multipart_parenthetized_element(self):
        elements = '(((abc def)))'
        expected = [[[['abc', 'def']]]]
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_nested_parenthetized_elements(self):
        elements = 'abc def (ghi (jkl mno) pqr) stu'
        expected = ['abc', 'def', ['ghi', ['jkl', 'mno'], 'pqr'], 'stu']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_starting_parenthetized_elements(self):
        elements = '((abc def) ghi) jkl mno pqr stu'
        expected = [[['abc', 'def'], 'ghi'], 'jkl', 'mno', 'pqr', 'stu']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_ending_parenthetized_elements(self):
        elements = 'abc def ghi jkl ((mno pqr) stu)'
        expected = ['abc', 'def', 'ghi', 'jkl', [['mno', 'pqr'], 'stu']]
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_bracketed_elements(self):
        elements = 'abc def [ghi jkl] mno'
        expected = ['abc', 'def', '[', ['ghi', 'jkl'], ']', 'mno']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_single_bracketed_element(self):
        elements = '[abc]'
        expected = ['[', ['abc'], ']']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_single_multipart_bracketed_element(self):
        elements = '[abc def]'
        expected = ['[', ['abc', 'def'], ']']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_single_nested_bracketed_element(self):
        elements = '[[[abc]]]'
        expected = ['[', ['[', ['[', ['abc'], ']'], ']'], ']']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_single_nested_multipart_bracketed_element(self):
        elements = '[[[abc def]]]'
        expected = ['[', ['[', ['[', ['abc', 'def'], ']'], ']'], ']']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_nested_bracketed_elements(self):
        elements = 'abc def [ghi [jkl mno] pqr] stu'
        expected = ['abc', 'def', '[', ['ghi', '[', ['jkl', 'mno'], ']', 'pqr'], ']', 'stu']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_starting_bracketed_elements(self):
        elements = '[[abc def] ghi] jkl mno pqr stu'
        expected = ['[', ['[', ['abc', 'def'], ']', 'ghi'], ']', 'jkl', 'mno', 'pqr', 'stu']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_ending_bracketed_elements(self):
        elements = 'abc def ghi jkl [[mno pqr] stu]'
        expected = ['abc', 'def', 'ghi', 'jkl', '[', ['[', ['mno', 'pqr'], ']', 'stu'], ']']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_single_multipart_bracketed_element_with_parentheses(self):
        elements = '[abc (def ghi)]'
        expected = ['[', ['abc', ['def', 'ghi']], ']']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_repetition(self):
        elements = '*abc'
        expected = ['*', 'abc']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_N_plus_repetition(self):
        elements = '5*abc'
        expected = ['5*', 'abc']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_N_minus_repetition(self):
        elements = '*5abc'
        expected = ['*5', 'abc']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_repetition_with_parentheses(self):
        elements = '*(abc def)'
        expected = ['*', ['abc', 'def']]
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_or(self):
        elements = 'abc / def'
        expected = ['abc', '/', 'def']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_multi_or(self):
        elements = 'abc / def / ghi'
        expected = ['abc', '/', 'def', '/', 'ghi']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_parenthetized_or(self):
        elements = 'abc / (def / ghi)'
        expected = ['abc', '/', ['def', '/', 'ghi']]
        self.assertEqual(choices_parser.split_into_parts(elements), expected)

    def test_bracketed_or(self):
        elements = 'abc / [def / ghi]'
        expected = ['abc', '/', '[', ['def', '/', 'ghi'], ']']
        self.assertEqual(choices_parser.split_into_parts(elements), expected)
