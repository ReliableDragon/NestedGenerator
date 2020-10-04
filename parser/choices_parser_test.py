import unittest
import logging

from state_machine import Edge, State
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

class ApplyRepetitionTestCase(unittest.TestCase):

    def test_no_repetition(self):
        edge = Edge('a', 'state_a')
        state = State('state_a')
        repetition = None
        expected = [state]
        self.assertEqual(choices_parser.apply_repetition(edge, state, repetition), expected)

    def test_N_repetition(self):
        edge = Edge('a', 'state_a')
        edge_2 = Edge('a', 'state_a_2')
        state = State('state_a', [edge_2])
        state_2 = State('state_a_2')
        repetition = (2, 2)
        expected = [state, state_2]
        self.assertTrue(states_equal(choices_parser.apply_repetition(edge, state, repetition), expected))

    def test_range_repetition(self):
        edge = Edge('a', 'state_a')
        edge2 = Edge('a', 'state_a_2')
        edge3 = Edge('a', 'state_a_3')
        edge3e = Edge('', 'state_a_3')
        state = State('state_a', [edge2])
        state2 = State('state_a_2', [edge3, edge3e])
        state3 = State('state_a_3')
        repetition = (2, 3)
        expected = [state, state2, state3]
        self.assertTrue(states_equal(choices_parser.apply_repetition(edge, state, repetition), expected))

    def test_N_minus_repetition(self):
        edge = Edge('a', 'state_a')
        edge2 = Edge('a', 'state_a_2')
        edge3 = Edge('a', 'state_a_3')
        edge3e = Edge('', 'state_a_3')
        state = State('state_a', [edge2, edge3e])
        state2 = State('state_a_2', [edge3, edge3e])
        state3 = State('state_a_3')
        repetition = (0, 3)
        expected = [state, state2, state3]
        self.assertTrue(states_equal(choices_parser.apply_repetition(edge, state, repetition), expected))

    def test_N_plus_repetition(self):
        edge = Edge('a', 'state_a')
        edge2 = Edge('a', 'state_a_2')
        edge3 = Edge('a', 'state_a_3')
        edge3e = Edge('', 'state_a_3')
        state = State('state_a', [edge2])
        state2 = State('state_a_2', [edge3])
        state3 = State('state_a_3', [edge3])
        repetition = (3, float('inf'))
        expected = [state, state2, state3]
        self.assertTrue(states_equal(choices_parser.apply_repetition(edge, state, repetition), expected))

    def test_any_repetition(self):
        edge = Edge('a', 'state_a')
        state = State('state_a', [edge])
        repetition = (0, float('inf'))
        expected = [state]
        self.assertTrue(states_equal(choices_parser.apply_repetition(edge, state, repetition), expected))

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
        self.assertTrue(states_equal(actual[1], expected[1]))
        self.assertTrue(states_equal(actual[2], expected[2]))

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

        logger.debug(f'Actual result: {actual}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

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

        logger.debug(f'Actual result: {actual}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

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

        logger.debug(f'Actual result: {actual}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

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

        logger.debug(f'Actual result: {actual}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

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

        logger.debug(f'Actual result: {actual}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

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

        logger.debug(f'Actual result: {actual}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

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

        logger.debug(f'Actual result: {actual}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

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
        state3_2 = State('ghi_2', edge2_e)

        start_edges = [edge, edge2]
        end_states = [state2_2, state3_2]
        states = [state, state2, state3]
        expected = (start_edges, end_states, states)
        actual = choices_parser.recursive_parse_elements(elements)

        logger.debug(f'Actual result: {actual}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

def states_equal(states1, states2):
    logger.debug(f'Comparing states:\n{states1}\n{states2}')
    if not isinstance(states1, list):
        states1 = [states1]
    if not isinstance(states2, list):
        states2 = [states2]

    if not len(states1) == len(states2):
        logger.debug('State list lengths are not equal!')
        return False

    for i in range(len(states1)):
        state1 = states1[i]
        state2 = states2[i]
        equal = True

        if not state1.id == state2.id:
            logger.debug(f'States do not have equal IDs:\n{state1}\n{state2}')
            return False
        if not state1.is_automata == state2.is_automata:
            logger.debug(f'States do not have equal is_automata:\n{state1}\n{state2}')
            return False
        if not len(state1.edges) == len(state2.edges):
            logger.debug(f'States do not have equal edge list lengths:\n{state1}\n{state2}')
            return False
        for j in range(len(state1.edges)):
            edge1 = state1.edges[j]
            edge2 = state2.edges[j]
            if not edge1.input == edge2.input:
                logger.debug(f'States {state1.id} and {state2.id} have mismatching inputs for edges at index {j}:\n{edge1}\n{edge2}')
                return False
            if not edge1.dest == edge2.dest:
                logger.debug(f'States {state1.id} and {state2.id} have mismatching inputs for edges at index {j}:\n{edge1}\n{edge2}')
                return False
            if not edge1.is_character_class == edge2.is_character_class:
                logger.debug(f'States {state1.id} and {state2.id} have mismatching inputs for edges at index {j}:\n{edge1}\n{edge2}')
                return False
    return True

def edges_equal(edges1, edges2):
    logger.debug(f'Comparing edges:\n{edges1}\n{edges2}')
    if not len(edges1) == len(edges2):
        logger.debug(f'States do not have equal edge list lengths:\n{edges1}\n{edges2}')
        return False
    for j in range(len(edges1)):
        edge1 = edges1[j]
        edge2 = edges2[j]
        if not edge1.input == edge2.input:
            logger.debug(f'Edge lists {edges1} and {edges2} have mismatching inputs for edges at index {j}:\n{edge1}\n{edge2}')
            return False
        if not edge1.dest == edge2.dest:
            logger.debug(f'Edge lists {edges1} and {edges2} have mismatching inputs for edges at index {j}:\n{edge1}\n{edge2}')
            return False
        if not edge1.is_character_class == edge2.is_character_class:
            logger.debug(f'Edge lists {edges1} and {edges2} have mismatching inputs for edges at index {j}:\n{edge1}\n{edge2}')
            return False
    return True
