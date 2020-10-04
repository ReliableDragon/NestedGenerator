import unittest
import logging

import elements_splitter

logging.basicConfig(level=logging.DEBUG)

class BasicSplitterTestCase(unittest.TestCase):

    def test_empty_elements(self):
        elements = ''
        self.assertEqual(elements_splitter.split_into_tokens(elements), [])

    def test_single_elements(self):
        elements = 'abc'
        self.assertEqual(elements_splitter.split_into_tokens(elements), ['abc'])

    def test_simple_elements(self):
        elements = 'abc def ghi'
        self.assertEqual(elements_splitter.split_into_tokens(elements), ['abc', 'def', 'ghi'])

    def test_quoted_elements(self):
        elements = 'abc def "*([ghi jkl])*" mno'
        expected = ['abc', 'def', '"*([ghi jkl])*"', 'mno']
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_starting_quoted_elements(self):
        elements = '"abc def" ghi jkl mno'
        expected = ['"abc def"', 'ghi', 'jkl', 'mno']
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_ending_quoted_elements(self):
        elements = 'abc def ghi "jkl mno"'
        expected = ['abc', 'def', 'ghi', '"jkl mno"']
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)


class ParenthesesSplitterTestCase(unittest.TestCase):
    def test_parenthetized_elements(self):
        elements = 'abc def (ghi jkl) mno'
        expected = ['abc', 'def', ['ghi', 'jkl'], 'mno']
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_single_parenthetized_element(self):
        elements = '(abc)'
        expected = [['abc']]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_single_multipart_parenthetized_element(self):
        elements = '(abc def)'
        expected = [['abc', 'def']]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_single_nested_parenthetized_element(self):
        elements = '(((abc)))'
        expected = [[[['abc']]]]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_single_nested_multipart_parenthetized_element(self):
        elements = '(((abc def)))'
        expected = [[[['abc', 'def']]]]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_nested_parenthetized_elements(self):
        elements = 'abc def (ghi (jkl mno) pqr) stu'
        expected = ['abc', 'def', ['ghi', ['jkl', 'mno'], 'pqr'], 'stu']
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_starting_parenthetized_elements(self):
        elements = '((abc def) ghi) jkl mno pqr stu'
        expected = [[['abc', 'def'], 'ghi'], 'jkl', 'mno', 'pqr', 'stu']
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_ending_parenthetized_elements(self):
        elements = 'abc def ghi jkl ((mno pqr) stu)'
        expected = ['abc', 'def', 'ghi', 'jkl', [['mno', 'pqr'], 'stu']]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)


class BracketedSplitterTestCase(unittest.TestCase):
    def test_bracketed_elements(self):
        elements = 'abc def [ghi jkl] mno'
        expected = ['abc', 'def', ['[', 'ghi', 'jkl', ']'], 'mno']
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_single_bracketed_element(self):
        elements = '[abc]'
        expected = [['[', 'abc', ']']]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_single_multipart_bracketed_element(self):
        elements = '[abc def]'
        expected = [['[', 'abc', 'def', ']']]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_single_nested_bracketed_element(self):
        elements = '[[[abc]]]'
        expected = [['[', ['[', ['[', 'abc', ']'], ']'], ']']]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_single_nested_multipart_bracketed_element(self):
        elements = '[[[abc def]]]'
        expected = [['[', ['[', ['[', 'abc', 'def', ']'], ']'], ']']]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_nested_bracketed_elements(self):
        elements = 'abc def [ghi [jkl mno] pqr] stu'
        expected = ['abc', 'def', ['[', 'ghi', ['[', 'jkl', 'mno', ']'], 'pqr', ']'], 'stu']
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_starting_bracketed_elements(self):
        elements = '[[abc def] ghi] jkl mno pqr stu'
        expected = [['[', ['[', 'abc', 'def', ']'], 'ghi', ']'], 'jkl', 'mno', 'pqr', 'stu']
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_ending_bracketed_elements(self):
        elements = 'abc def ghi jkl [[mno pqr] stu]'
        expected = ['abc', 'def', 'ghi', 'jkl', ['[', ['[', 'mno', 'pqr', ']'], 'stu', ']']]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_single_multipart_bracketed_element_with_parentheses(self):
        elements = '[abc (def ghi)]'
        expected = [['[', 'abc', ['def', 'ghi'], ']']]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)


class RepetitionSplitterTestCase(unittest.TestCase):
    def test_repetition(self):
        elements = '*abc'
        expected = [['*', 'abc']]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_N_repetition(self):
        elements = '10abc'
        expected = [['10', 'abc']]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_N_plus_repetition(self):
        elements = '5*abc'
        expected = [['5*', 'abc']]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_N_minus_repetition(self):
        elements = '*5abc'
        expected = [['*5', 'abc']]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_repetition_with_parentheses(self):
        elements = '*(abc def)'
        expected = [['*', ['abc', 'def']]]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_N_repetition_with_parentheses(self):
        elements = '10(abc def)'
        expected = [['10', ['abc', 'def']]]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)


class AlternativesSplitterTestCase(unittest.TestCase):
    def test_or(self):
        elements = 'abc / def'
        expected = ['abc', '/', 'def']
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_multi_or(self):
        elements = 'abc / def / ghi'
        expected = ['abc', '/', 'def', '/', 'ghi']
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_parenthetized_or(self):
        elements = 'abc / (def / ghi)'
        expected = ['abc', '/', ['def', '/', 'ghi']]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)

    def test_bracketed_or(self):
        elements = 'abc / [def / ghi]'
        expected = ['abc', '/', ['[', 'def', '/', 'ghi', ']']]
        self.assertEqual(elements_splitter.split_into_tokens(elements), expected)
