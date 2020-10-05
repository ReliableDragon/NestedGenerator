import unittest
import logging

from state_machine import Edge, State, StateMachine, START_STATE, FINAL_STATE
from state_machine_test_helper import assert_states_equal, edges_equal, assert_state_machines_equal
import choices_parser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class GetConcurrentTokensTestCase(unittest.TestCase):

    def test_no_concurrency(self):
        elements = ['abc', 'def', 'ghi']
        expected = ['abc'], 1
        self.assertEqual(choices_parser.get_concurrent_tokens(elements, 0), expected)

    def test_one_concurrency(self):
        elements = ['abc', '/', 'def', 'ghi']
        expected = ['abc', 'def'], 3
        self.assertEqual(choices_parser.get_concurrent_tokens(elements, 0), expected)

    def test_all_concurrency(self):
        elements = ['abc', '/', 'def', '/', 'ghi']
        expected = ['abc', 'def', 'ghi'], 5
        self.assertEqual(choices_parser.get_concurrent_tokens(elements, 0), expected)

    def test_concurrency_with_parens(self):
        elements = ['abc', '/', 'def', '/', ['ghi', '/', 'jkl']]
        expected = ['abc', 'def', ['ghi', '/', 'jkl']], 5
        self.assertEqual(choices_parser.get_concurrent_tokens(elements, 0), expected)

    def test_concurrency_with_repetition(self):
        elements = ['abc', '/', ['3*8', 'def'], 'ghi']
        expected = ['abc', ['3*8', 'def']], 3
        self.assertEqual(choices_parser.get_concurrent_tokens(elements, 0), expected)

    def test_concurrency_with_optional(self):
        elements = ['abc', '/', 'def', '/', ['ghi', '/', 'jkl']]
        expected = ['abc', 'def', ['ghi', '/', 'jkl']], 5
        self.assertEqual(choices_parser.get_concurrent_tokens(elements, 0), expected)

    def test_concurrency_starts_with_repetition(self):
        elements = [['5*8', 'abc'], '/', 'def', 'ghi']
        expected = [['5*8', 'abc'], 'def'], 3
        self.assertEqual(choices_parser.get_concurrent_tokens(elements, 0), expected)

    def test_concurrency_start_position(self):
        elements = ['abc', '/', 'def', 'ghi']
        expected = ['ghi'], 4
        self.assertEqual(choices_parser.get_concurrent_tokens(elements, 3), expected)

class GetRepetitionTestCase(unittest.TestCase):
    def test_no_repetition(self):
        element = 'abc'
        expected = 'abc', None
        self.assertEqual(choices_parser.get_repetition(element), expected)

    def test_N_repetition(self):
        element = ['4', 'abc']
        expected = 'abc', (4, 4)
        self.assertEqual(choices_parser.get_repetition(element), expected)

    def test_N_plus_repetition(self):
        element = ['4*', 'abc']
        expected = 'abc', (4, float('inf'))
        self.assertEqual(choices_parser.get_repetition(element), expected)

    def test_N_minus_repetition(self):
        element = ['*4', 'abc']
        expected = 'abc', (0, 4)
        self.assertEqual(choices_parser.get_repetition(element), expected)

    def test_any_repetition(self):
        element = ['*', 'abc']
        expected = 'abc', (0, float('inf'))
        self.assertEqual(choices_parser.get_repetition(element), expected)

class GetOptionalityTestCase(unittest.TestCase):
    def test_no_optionality(self):
        element = 'abc'
        expected = 'abc', False
        self.assertEqual(choices_parser.get_optionality(element), expected)

    def test_simple_optionality(self):
        element = ['[', 'abc', ']']
        expected = 'abc', True
        self.assertEqual(choices_parser.get_optionality(element), expected)

    def test_nested_optionality(self):
        element = ['[', ['[', 'abc', ']'], ']']
        expected = ['[', 'abc', ']'], True
        self.assertEqual(choices_parser.get_optionality(element), expected)

    def test_repeated_optionality(self):
        element = ['[', ['5*8', 'abc'], ']']
        expected = ['5*8', 'abc'], True
        self.assertEqual(choices_parser.get_optionality(element), expected)

class RecursiveParseElementsTestCase(unittest.TestCase):

    def test_trivial_case(self):
        elements = ['abc']
        edge = Edge('abc', 'abc')
        state = State('abc', is_automata=True)
        start_edges = [edge]
        end_states = [state]
        states = [state]
        expected = (start_edges, end_states, states)
        actual = choices_parser.recursive_parse_elements(elements)

        self.assertTrue(edges_equal(actual[0], expected[0]))
        assert_states_equal(actual[1], expected[1])
        assert_states_equal(actual[2], expected[2])

    def test_two_token_case(self):
        elements = ['abc', '"def"']
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        state = State('abc', edge2, is_automata=True)
        state2 = State('def')

        start_edges = [edge]
        end_states = [state2]
        states = [state, state2]
        expected = (start_edges, end_states, states)
        actual = choices_parser.recursive_parse_elements(elements)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        assert_states_equal(actual[1], expected[1])
        logger.debug(f'states')
        assert_states_equal(actual[2], expected[2])

    def test_two_alternative_tokens_case(self):
        elements = ['abc', '/', '"def"']
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        state = State('abc', is_automata=True)
        state2 = State('def')

        start_edges = [edge, edge2]
        end_states = [state, state2]
        states = [state, state2]
        expected = (start_edges, end_states, states)
        actual = choices_parser.recursive_parse_elements(elements)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        assert_states_equal(actual[1], expected[1])
        logger.debug(f'states')
        assert_states_equal(actual[2], expected[2])

    def test_parenthized_tokens_case(self):
        elements = ['abc', ['"def"', '"ghi"']]
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        edge3 = Edge('ghi', 'ghi')
        state = State('abc', edge2, is_automata=True)
        state2 = State('def', edge3)
        state3 = State('ghi')

        start_edges = [edge]
        end_states = [state3]
        states = [state, state2, state3]
        expected = (start_edges, end_states, states)
        actual = choices_parser.recursive_parse_elements(elements)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        assert_states_equal(actual[1], expected[1])
        logger.debug(f'states')
        assert_states_equal(actual[2], expected[2])

    def test_starting_parenthized_tokens_case(self):
        elements = [['abc', '"def"'], '"ghi"']
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        edge3 = Edge('ghi', 'ghi')
        state = State('abc', edge2, is_automata=True)
        state2 = State('def', edge3)
        state3 = State('ghi')

        start_edges = [edge]
        end_states = [state3]
        states = [state, state2, state3]
        expected = (start_edges, end_states, states)
        actual = choices_parser.recursive_parse_elements(elements)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        assert_states_equal(actual[1], expected[1])
        logger.debug(f'states')
        assert_states_equal(actual[2], expected[2])

    def test_identical_parenthetized_token_case(self):
        elements = ['abc', ['abc']]
        edge = Edge('abc', 'abc')
        edge2 = Edge('abc', 'abc_#2')
        state = State('abc', edge2, is_automata=True)
        state2 = State('abc_#2', is_automata=True)

        start_edges = [edge]
        end_states = [state2]
        states = [state, state2]
        expected = (start_edges, end_states, states)
        actual = choices_parser.recursive_parse_elements(elements)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        assert_states_equal(actual[1], expected[1])
        logger.debug(f'states')
        assert_states_equal(actual[2], expected[2])

    def test_parenthized_alternative_tokens_case(self):
        elements = ['abc', ['"def"', '/', '"ghi"']]
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        edge3 = Edge('ghi', 'ghi')
        state = State('abc', [edge2, edge3], is_automata=True)
        state2 = State('def')
        state3 = State('ghi')

        start_edges = [edge]
        end_states = [state2, state3]
        states = [state, state2, state3]
        expected = (start_edges, end_states, states)
        actual = choices_parser.recursive_parse_elements(elements)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        assert_states_equal(actual[1], expected[1])
        logger.debug(f'states')
        assert_states_equal(actual[2], expected[2])

    def test_N_repeated_token_case(self):
        elements = ['abc', ['2', '"def"']]
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        edge2_2 = Edge('def', 'def_2')
        state = State('abc', edge2, is_automata=True)
        state2 = State('def', edge2_2)
        state2_2 = State('def_2')

        start_edges = [edge]
        end_states = [state2_2]
        states = [state, state2, state2_2]
        expected = (start_edges, end_states, states)
        actual = choices_parser.recursive_parse_elements(elements)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        assert_states_equal(actual[1], expected[1])
        logger.debug(f'states')
        assert_states_equal(actual[2], expected[2])

    def test_repeated_token_case(self):
        elements = ['abc', ['*', '"def"']]
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        edge2i = Edge('', 'def')
        state = State('abc', [edge2, edge2i], is_automata=True)
        state2 = State('def', [edge2])

        start_edges = [edge]
        end_states = [state2]
        states = [state, state2]
        expected = (start_edges, end_states, states)
        actual = choices_parser.recursive_parse_elements(elements)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        assert_states_equal(actual[1], expected[1])
        logger.debug(f'states')
        assert_states_equal(actual[2], expected[2])

    def test_parenthized_alternative_repeated_tokens_case(self):
        elements = ['abc', '/', ['2*', ['"def"', '"ghi"']]]
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        edge3 = Edge('ghi', 'ghi')
        edge2_2 = Edge('def', 'def_2')
        edge3_2 = Edge('ghi', 'ghi_2')
        edge2_2 = Edge('def', 'def_2')
        edge2_e = Edge('def', 'def_2')
        edge3_2 = Edge('ghi', 'ghi_2')
        state = State('abc', is_automata=True)
        state2 = State('def', edge3)
        state3 = State('ghi', edge2_2)
        state2_2 = State('def_2', edge3_2)
        state3_2 = State('ghi_2', edge2_2)

        start_edges = [edge, edge2]
        end_states = [state, state3_2]
        states = [state, state2, state3, state2_2, state3_2]
        expected = (start_edges, end_states, states)
        actual = choices_parser.recursive_parse_elements(elements)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        assert_states_equal(actual[1], expected[1])
        logger.debug(f'states')
        assert_states_equal(actual[2], expected[2])

    def test_parenthized_alternative_repeated_alternative_tokens_case(self):
        elements = ['abc', '/', ['2*', ['"def"', '/', '"ghi"']]]
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        edge3 = Edge('ghi', 'ghi')
        edge2_2 = Edge('def', 'def_2')
        edge3_2 = Edge('ghi', 'ghi_2')
        edge2_2 = Edge('def', 'def_2')
        edge2_e = Edge('def', 'def_2')
        edge3_2 = Edge('ghi', 'ghi_2')
        state = State('abc', is_automata=True)
        state2 = State('def', [edge2_2, edge3_2])
        state3 = State('ghi', [edge2_2, edge3_2])
        state2_2 = State('def_2', [edge2_2, edge3_2])
        state3_2 = State('ghi_2', [edge2_2, edge3_2])

        start_edges = [edge, edge2, edge3]
        end_states = [state, state2_2, state3_2]
        states = [state, state2, state3, state2_2, state3_2]
        expected = (start_edges, end_states, states)
        actual = choices_parser.recursive_parse_elements(elements)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        assert_states_equal(actual[1], expected[1])
        logger.debug(f'states')
        assert_states_equal(actual[2], expected[2])

class ParseElementsTestCase(unittest.TestCase):

    def test_trivial_case(self):
        rulename = 'rulename'
        elements = 'abc'
        edge = Edge('abc', 'abc')
        final_edge = Edge('', FINAL_STATE)
        state = State('abc', final_edge, is_automata=True)
        start_state = State(START_STATE, edge)
        final_state = State(FINAL_STATE)

        states = [start_state, state, final_state]
        expected = StateMachine(rulename, states)
        actual = choices_parser.parse_elements(rulename, elements)

        assert_state_machines_equal(actual, expected)

    def test_two_token_case(self):
        rulename = 'rulename'
        elements = 'abc "def"'
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        final_edge = Edge('', FINAL_STATE)
        state = State('abc', edge2, is_automata=True)
        state2 = State('def', final_edge)
        start_state = State(START_STATE, edge)
        final_state = State(FINAL_STATE)

        states = [start_state, state, state2, final_state]
        expected = StateMachine(rulename, states)
        actual = choices_parser.parse_elements(rulename, elements)

        assert_state_machines_equal(actual, expected)

    def test_two_alternative_tokens_case(self):
        rulename = 'rulename'
        elements = 'abc / "def"'
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        final_edge = Edge('', FINAL_STATE)
        state = State('abc', final_edge, is_automata=True)
        state2 = State('def', final_edge)
        start_state = State(START_STATE, [edge, edge2])
        final_state = State(FINAL_STATE)

        states = [start_state, state, state2, final_state]
        expected = StateMachine(rulename, states)
        actual = choices_parser.parse_elements(rulename, elements)

        assert_state_machines_equal(actual, expected)

    def test_optional_token_case(self):
        rulename = 'rulename'
        elements = 'abc ["def"]'
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        edge2_e = Edge('', 'def')
        final_edge = Edge('', FINAL_STATE)
        state = State('abc', [edge2, edge2_e], is_automata=True)
        state2 = State('def', final_edge)
        start_state = State(START_STATE, edge)
        final_state = State(FINAL_STATE)

        states = [start_state, state, state2, final_state]
        expected = StateMachine(rulename, states)
        actual = choices_parser.parse_elements(rulename, elements)

        assert_state_machines_equal(actual, expected)

    def test_parenthized_tokens_case(self):
        rulename = 'rulename'
        elements = 'abc ("def" "ghi")'
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        edge3 = Edge('ghi', 'ghi')
        final_edge = Edge('', FINAL_STATE)
        state = State('abc', edge2, is_automata=True)
        state2 = State('def', edge3)
        state3 = State('ghi', final_edge)
        start_state = State(START_STATE, edge)
        final_state = State(FINAL_STATE)

        states = [start_state, state, state2, state3, final_state]
        expected = StateMachine(rulename, states)
        actual = choices_parser.parse_elements(rulename, elements)

        assert_state_machines_equal(actual, expected)

    def test_starting_parenthized_tokens_case(self):
        rulename = 'rulename'
        elements = '(abc "def") "ghi"'
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        edge3 = Edge('ghi', 'ghi')
        final_edge = Edge('', FINAL_STATE)
        state = State('abc', edge2, is_automata=True)
        state2 = State('def', edge3)
        state3 = State('ghi', final_edge)
        start_state = State(START_STATE, edge)
        final_state = State(FINAL_STATE)

        states = [start_state, state, state2, state3, final_state]
        expected = StateMachine(rulename, states)
        actual = choices_parser.parse_elements(rulename, elements)

        assert_state_machines_equal(actual, expected)

    def test_identical_parenthetized_token_case(self):
        rulename = 'rulename'
        elements = 'abc (abc)'
        edge = Edge('abc', 'abc')
        edge2 = Edge('abc', 'abc_#2')
        final_edge = Edge('', FINAL_STATE)
        state = State('abc', edge2, is_automata=True)
        state2 = State('abc_#2', final_edge, is_automata=True)
        start_state = State(START_STATE, edge)
        final_state = State(FINAL_STATE)

        states = [start_state, state, state2, final_state]
        expected = StateMachine(rulename, states)
        actual = choices_parser.parse_elements(rulename, elements)

        assert_state_machines_equal(actual, expected)

    def test_parenthized_alternative_tokens_case(self):
        rulename = 'rulename'
        elements = 'abc ("def" / "ghi")'
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        edge3 = Edge('ghi', 'ghi')
        final_edge = Edge('', FINAL_STATE)
        state = State('abc', [edge2, edge3], is_automata=True)
        state2 = State('def', final_edge)
        state3 = State('ghi', final_edge)
        start_state = State(START_STATE, edge)
        final_state = State(FINAL_STATE)

        states = [start_state, state, state2, state3, final_state]
        expected = StateMachine(rulename, states)
        actual = choices_parser.parse_elements(rulename, elements)

        assert_state_machines_equal(actual, expected)

    def test_N_repeated_token_case(self):
        rulename = 'rulename'
        elements = 'abc 2"def"'
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        edge2_2 = Edge('def', 'def_2')
        final_edge = Edge('', FINAL_STATE)
        state = State('abc', edge2, is_automata=True)
        state2 = State('def', edge2_2)
        state2_2 = State('def_2', final_edge)
        start_state = State(START_STATE, edge)
        final_state = State(FINAL_STATE)

        states = [start_state, state, state2, state2_2, final_state]
        expected = StateMachine(rulename, states)
        actual = choices_parser.parse_elements(rulename, elements)

        assert_state_machines_equal(actual, expected)

    def test_repeated_token_case(self):
        rulename = 'rulename'
        elements = 'abc *"def"'
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        edge2i = Edge('', 'def')
        final_edge = Edge('', FINAL_STATE)
        state = State('abc', [edge2, edge2i], is_automata=True)
        state2 = State('def', [edge2, final_edge])
        start_state = State(START_STATE, edge)
        final_state = State(FINAL_STATE)

        states = [start_state, state, state2, final_state]
        expected = StateMachine(rulename, states)
        actual = choices_parser.parse_elements(rulename, elements)

        assert_state_machines_equal(actual, expected)

    def test_parenthized_alternative_repeated_tokens_case(self):
        rulename = 'rulename'
        elements = 'abc / 2*("def" "ghi")'
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        edge3 = Edge('ghi', 'ghi')
        edge2_2 = Edge('def', 'def_2')
        edge3_2 = Edge('ghi', 'ghi_2')
        edge2_2 = Edge('def', 'def_2')
        edge2_e = Edge('def', 'def_2')
        edge3_2 = Edge('ghi', 'ghi_2')
        final_edge = Edge('', FINAL_STATE)
        state = State('abc', final_edge, is_automata=True)
        state2 = State('def', edge3)
        state3 = State('ghi', edge2_2)
        state2_2 = State('def_2', edge3_2)
        state3_2 = State('ghi_2', [edge2_2, final_edge])
        start_state = State(START_STATE, [edge, edge2])
        final_state = State(FINAL_STATE)

        states = [start_state, state, state2, state3, state2_2, state3_2, final_state]
        expected = StateMachine(rulename, states)
        actual = choices_parser.parse_elements(rulename, elements)

        assert_state_machines_equal(actual, expected)

    def test_parenthized_alternative_repeated_alternative_tokens_case(self):
        rulename = 'rulename'
        elements = 'abc / 2*("def" / "ghi")'
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        edge3 = Edge('ghi', 'ghi')
        edge2_2 = Edge('def', 'def_2')
        edge3_2 = Edge('ghi', 'ghi_2')
        edge2_2 = Edge('def', 'def_2')
        edge2_e = Edge('def', 'def_2')
        edge3_2 = Edge('ghi', 'ghi_2')
        final_edge = Edge('', FINAL_STATE)
        state = State('abc', final_edge, is_automata=True)
        state2 = State('def', [edge2_2, edge3_2])
        state3 = State('ghi', [edge2_2, edge3_2])
        state2_2 = State('def_2', [edge2_2, edge3_2, final_edge])
        state3_2 = State('ghi_2', [edge2_2, edge3_2, final_edge])
        start_state = State(START_STATE, [edge, edge2, edge3])
        final_state = State(FINAL_STATE)

        states = [start_state, state, state2, state3, state2_2, state3_2, final_state]
        expected = StateMachine(rulename, states)
        actual = choices_parser.parse_elements(rulename, elements)

        assert_state_machines_equal(actual, expected)

class ParseFromStringTestCase(unittest.TestCase):

    def test_trivial_case(self):
        grammar = 'rulename = abc "def"\nabc = "abc"'

        rulename = 'rulename'
        edge = Edge('abc', 'abc')
        edge2 = Edge('def', 'def')
        final_edge = Edge('', FINAL_STATE)
        state = State('abc', edge2, is_automata=True)
        state2 = State('def', final_edge)
        start_state = State(START_STATE, edge)
        final_state = State(FINAL_STATE)
        states = [start_state, state, state2, final_state]
        expected = StateMachine(rulename, states)

        rulename = 'abc'
        sub_edge = Edge('abc', 'abc')
        sub_final_edge = Edge('', FINAL_STATE)
        sub_state = State('abc', sub_final_edge)
        sub_start_state = State(START_STATE, sub_edge)
        sub_final_state = State(FINAL_STATE)
        states = [sub_start_state, sub_state, sub_final_state]
        submachine = StateMachine(rulename, states)

        expected.register_automata(submachine)

        actual = choices_parser.parse_from_string(grammar)

        logger.debug(f'Actual: {actual}')
        logger.debug(f'Expected: {expected}')
        assert_state_machines_equal(actual, expected)
