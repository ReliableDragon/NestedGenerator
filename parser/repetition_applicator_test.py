import unittest
import logging

from state_machine import Edge, State
from state_machine_test_helper import states_equal, edges_equal
import repetition_applicator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class ApplyRepetitionSingleTokenTestCase(unittest.TestCase):

    def test_no_repetition(self):
        edge = Edge('a', 'state_a')
        state = State('state_a')

        edge_out = Edge('a', 'state_a')
        state_out = State('state_a')

        in_edges = [edge]
        new_end_states = [state]
        new_states = [state]
        repetition = None
        is_optional = False

        in_edges_out = [edge_out]
        new_end_states_out = [state_out]
        new_states_out = [state_out]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_optional_repetition(self):
        edge = Edge('a', 'state_a')
        state = State('state_a')

        edge_out = Edge('a', 'state_a')
        edge_out_e = Edge('', 'state_a')
        state_out = State('state_a')

        in_edges = [edge]
        new_end_states = [state]
        new_states = [state]
        repetition = None
        is_optional = True

        in_edges_out = [edge_out, edge_out_e]
        new_end_states_out = [state_out]
        new_states_out = [state_out]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_N_repetition(self):
        edge = Edge('a', 'state_a')
        state = State('state_a')

        edge_out = Edge('a', 'state_a')
        edge_2_out = Edge('a', 'state_a_2')
        state_out = State('state_a', [edge_2_out])
        state_2_out = State('state_a_2')

        in_edges = [edge]
        new_end_states = [state]
        new_states = [state]
        repetition = (2, 2)
        is_optional = False

        in_edges_out = [edge_out]
        new_end_states_out = [state_2_out]
        new_states_out = [state_out, state_2_out]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_range_repetition(self):
        in_edge = Edge('a', 'state_a')
        in_state = State('state_a')

        edge = Edge('a', 'state_a')
        edge2 = Edge('a', 'state_a_2')
        edge3 = Edge('a', 'state_a_3')
        edge3e = Edge('', 'state_a_3')
        state = State('state_a', [edge2])
        state2 = State('state_a_2', [edge3, edge3e])
        state3 = State('state_a_3')

        in_edges = [in_edge]
        new_end_states = [in_state]
        new_states = [in_state]
        repetition = (2, 3)
        is_optional = False

        in_edges_out = [edge]
        new_end_states_out = [state3]
        new_states_out = [state, state2, state3]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_range_repetition(self):
        in_edge = Edge('a', 'state_a')
        in_state = State('state_a')

        edge = Edge('a', 'state_a')
        edge2 = Edge('a', 'state_a_2')
        edge3 = Edge('a', 'state_a_3')
        edge3e = Edge('', 'state_a_3')
        state = State('state_a', [edge2, edge3e])
        state2 = State('state_a_2', [edge3, edge3e])
        state3 = State('state_a_3')

        in_edges = [in_edge]
        new_end_states = [in_state]
        new_states = [in_state]
        repetition = (1, 3)
        is_optional = False

        in_edges_out = [edge]
        new_end_states_out = [state3]
        new_states_out = [state, state2, state3]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_N_minus_repetition(self):
        in_edge = Edge('a', 'state_a')
        in_state = State('state_a')

        edge = Edge('a', 'state_a')
        edge2 = Edge('a', 'state_a_2')
        edge3 = Edge('a', 'state_a_3')
        edge3e = Edge('', 'state_a_3')
        state = State('state_a', [edge2, edge3e])
        state2 = State('state_a_2', [edge3, edge3e])
        state3 = State('state_a_3')

        in_edges = [in_edge]
        new_end_states = [in_state]
        new_states = [in_state]
        repetition = (0, 3)
        is_optional = False

        in_edges_out = [edge, edge3e]
        new_end_states_out = [state3]
        new_states_out = [state, state2, state3]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_N_plus_repetition(self):
        in_edge = Edge('a', 'state_a')
        in_state = State('state_a')

        edge = Edge('a', 'state_a')
        edge2 = Edge('a', 'state_a_2')
        edge3 = Edge('a', 'state_a_3')
        edge3e = Edge('', 'state_a_3')
        state = State('state_a', [edge2])
        state2 = State('state_a_2', [edge3])
        state3 = State('state_a_3', [edge3])

        in_edges = [in_edge]
        new_end_states = [in_state]
        new_states = [in_state]
        repetition = (3, float('inf'))
        is_optional = False

        in_edges_out = [edge]
        new_end_states_out = [state3]
        new_states_out = [state, state2, state3]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_any_repetition(self):
        in_edge = Edge('a', 'state_a')
        in_edge_e = Edge('', 'state_a')
        in_state = State('state_a')

        edge = Edge('a', 'state_a')
        state = State('state_a', [edge])

        in_edges = [in_edge]
        new_end_states = [in_state]
        new_states = [in_state]
        repetition = (0, float('inf'))
        is_optional = False

        in_edges_out = [edge, in_edge_e]
        new_end_states_out = [state]
        new_states_out = [state]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

class ApplyRepetitionConsecutiveTokensTestCase(unittest.TestCase):

    def test_no_repetition(self):
        edge_a = Edge('a', 'state_a')
        edge_b = Edge('b', 'state_b')
        state_a = State('state_a', edge_b)
        state_b = State('state_b')

        edge_out_a = Edge('a', 'state_a')
        edge_out_b = Edge('b', 'state_b')
        state_out_a = State('state_a', edge_out_b)
        state_out_b = State('state_b')

        in_edges = [edge_a]
        new_end_states = [state_b]
        new_states = [state_a, state_b]
        repetition = None
        is_optional = False

        in_edges_out = [edge_out_a]
        new_end_states_out = [state_out_b]
        new_states_out = [state_out_a, state_out_b]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_optional_repetition(self):
        edge_a = Edge('a', 'state_a')
        edge_b = Edge('b', 'state_b')
        state_a = State('state_a', edge_b)
        state_b = State('state_b')

        edge_out_a = Edge('a', 'state_a')
        edge_out_b = Edge('b', 'state_b')
        edge_out_b_e = Edge('', 'state_b')
        state_out_a = State('state_a', edge_out_b)
        state_out_b = State('state_b')

        in_edges = [edge_a]
        new_end_states = [state_b]
        new_states = [state_a, state_b]
        repetition = None
        is_optional = True

        in_edges_out = [edge_out_a, edge_out_b_e]
        new_end_states_out = [state_out_b]
        new_states_out = [state_out_a, state_out_b]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_N_repetition(self):
        edge_a = Edge('a', 'state_a')
        edge_b = Edge('b', 'state_b')
        state_a = State('state_a', edge_b)
        state_b = State('state_b')

        edge_out_a = Edge('a', 'state_a')
        edge_out_b = Edge('b', 'state_b')
        edge_out_a_2 = Edge('a', 'state_a_2')
        edge_out_b_2 = Edge('b', 'state_b_2')
        state_out_a = State('state_a', edge_out_b)
        state_out_b = State('state_b', edge_out_a_2)
        state_out_a_2 = State('state_a_2', edge_out_b_2)
        state_out_b_2 = State('state_b_2')

        in_edges = [edge_a]
        new_end_states = [state_b]
        new_states = [state_a, state_b]
        repetition = (2, 2)
        is_optional = False

        in_edges_out = [edge_out_a]
        new_end_states_out = [state_out_b_2]
        new_states_out = [state_out_a, state_out_b, state_out_a_2, state_out_b_2]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_range_repetition(self):
        edge_a = Edge('a', 'state_a')
        edge_b = Edge('b', 'state_b')
        state_a = State('state_a', edge_b)
        state_b = State('state_b')

        edge_out_a = Edge('a', 'state_a')
        edge_out_b = Edge('b', 'state_b')
        edge_out_a_2 = Edge('a', 'state_a_2')
        edge_out_b_2 = Edge('b', 'state_b_2')
        edge_out_a_3 = Edge('a', 'state_a_3')
        edge_out_b_3 = Edge('b', 'state_b_3')
        edge_out_b_3_e = Edge('', 'state_b_3')
        state_out_a = State('state_a', edge_out_b)
        state_out_b = State('state_b', edge_out_a_2)
        state_out_a_2 = State('state_a_2', edge_out_b_2)
        state_out_b_2 = State('state_b_2', [edge_out_a_3, edge_out_b_3_e])
        state_out_a_3 = State('state_a_3', edge_out_b_3)
        state_out_b_3 = State('state_b_3')

        in_edges = [edge_a]
        new_end_states = [state_b]
        new_states = [state_a, state_b]
        repetition = (2, 3)
        is_optional = False

        in_edges_out = [edge_out_a]
        new_end_states_out = [state_out_b_3]
        new_states_out = [state_out_a, state_out_b, state_out_a_2, state_out_b_2, state_out_a_3, state_out_b_3]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_1_range_repetition(self):
        edge_a = Edge('a', 'state_a')
        edge_b = Edge('b', 'state_b')
        state_a = State('state_a', edge_b)
        state_b = State('state_b')

        edge_out_a = Edge('a', 'state_a')
        edge_out_b = Edge('b', 'state_b')
        edge_out_a_2 = Edge('a', 'state_a_2')
        edge_out_b_2 = Edge('b', 'state_b_2')
        edge_out_a_3 = Edge('a', 'state_a_3')
        edge_out_b_3 = Edge('b', 'state_b_3')
        edge_out_b_3_e = Edge('', 'state_b_3')
        state_out_a = State('state_a', edge_out_b)
        state_out_b = State('state_b', [edge_out_a_2, edge_out_b_3_e])
        state_out_a_2 = State('state_a_2', edge_out_b_2)
        state_out_b_2 = State('state_b_2', [edge_out_a_3, edge_out_b_3_e])
        state_out_a_3 = State('state_a_3', edge_out_b_3)
        state_out_b_3 = State('state_b_3')

        in_edges = [edge_a]
        new_end_states = [state_b]
        new_states = [state_a, state_b]
        repetition = (1, 3)
        is_optional = False

        in_edges_out = [edge_out_a]
        new_end_states_out = [state_out_b_3]
        new_states_out = [state_out_a, state_out_b, state_out_a_2, state_out_b_2, state_out_a_3, state_out_b_3]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_N_minus_repetition(self):
        edge_a = Edge('a', 'state_a')
        edge_b = Edge('b', 'state_b')
        state_a = State('state_a', edge_b)
        state_b = State('state_b')

        edge_out_a = Edge('a', 'state_a')
        edge_out_b = Edge('b', 'state_b')
        edge_out_a_2 = Edge('a', 'state_a_2')
        edge_out_b_2 = Edge('b', 'state_b_2')
        edge_out_a_3 = Edge('a', 'state_a_3')
        edge_out_b_3 = Edge('b', 'state_b_3')
        edge_out_b_3_e = Edge('', 'state_b_3')
        state_out_a = State('state_a', edge_out_b)
        state_out_b = State('state_b', [edge_out_a_2, edge_out_b_3_e])
        state_out_a_2 = State('state_a_2', edge_out_b_2)
        state_out_b_2 = State('state_b_2', [edge_out_a_3, edge_out_b_3_e])
        state_out_a_3 = State('state_a_3', edge_out_b_3)
        state_out_b_3 = State('state_b_3')

        in_edges = [edge_a]
        new_end_states = [state_b]
        new_states = [state_a, state_b]
        repetition = (0, 3)
        is_optional = False

        in_edges_out = [edge_out_a, edge_out_b_3_e]
        new_end_states_out = [state_out_b_3]
        new_states_out = [state_out_a, state_out_b, state_out_a_2, state_out_b_2, state_out_a_3, state_out_b_3]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_N_plus_repetition(self):
        edge_a = Edge('a', 'state_a')
        edge_b = Edge('b', 'state_b')
        state_a = State('state_a', edge_b)
        state_b = State('state_b')

        edge_out_a = Edge('a', 'state_a')
        edge_out_b = Edge('b', 'state_b')
        edge_out_a_2 = Edge('a', 'state_a_2')
        edge_out_b_2 = Edge('b', 'state_b_2')
        edge_out_a_3 = Edge('a', 'state_a_3')
        edge_out_a_3_i = Edge('a', 'state_a_3')
        edge_out_b_3 = Edge('b', 'state_b_3')
        state_out_a = State('state_a', edge_out_b)
        state_out_b = State('state_b', edge_out_a_2)
        state_out_a_2 = State('state_a_2', edge_out_b_2)
        state_out_b_2 = State('state_b_2', edge_out_a_3)
        state_out_a_3 = State('state_a_3', edge_out_b_3)
        state_out_b_3 = State('state_b_3', edge_out_a_3_i)

        in_edges = [edge_a]
        new_end_states = [state_b]
        new_states = [state_a, state_b]
        repetition = (3, float('inf'))
        is_optional = False

        in_edges_out = [edge_out_a]
        new_end_states_out = [state_out_b_3]
        new_states_out = [state_out_a, state_out_b, state_out_a_2, state_out_b_2, state_out_a_3, state_out_b_3]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_any_repetition(self):
        edge_a = Edge('a', 'state_a')
        edge_b = Edge('b', 'state_b')
        state_a = State('state_a', edge_b)
        state_b = State('state_b')

        edge_out_a = Edge('a', 'state_a')
        edge_out_a_i = Edge('a', 'state_a')
        edge_out_b = Edge('b', 'state_b')
        edge_out_b_e = Edge('', 'state_b')
        state_out_a = State('state_a', edge_out_b)
        state_out_b = State('state_b', edge_out_a_i)

        in_edges = [edge_a]
        new_end_states = [state_b]
        new_states = [state_a, state_b]
        repetition = (0, float('inf'))
        is_optional = False

        in_edges_out = [edge_out_a, edge_out_b_e]
        new_end_states_out = [state_out_b]
        new_states_out = [state_out_a, state_out_b]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

class ApplyRepetitionAlternativeTokensTestCase(unittest.TestCase):

    def test_no_repetition(self):
        edge_a = Edge('a', 'state_a')
        edge_b = Edge('b', 'state_b')
        state_a = State('state_a')
        state_b = State('state_b')

        edge_out_a = Edge('a', 'state_a')
        edge_out_b = Edge('b', 'state_b')
        state_out_a = State('state_a')
        state_out_b = State('state_b')

        in_edges = [edge_a, edge_b]
        new_end_states = [state_a, state_b]
        new_states = [state_a, state_b]
        repetition = None
        is_optional = False

        in_edges_out = [edge_out_a, edge_out_b]
        new_end_states_out = [state_out_a, state_out_b]
        new_states_out = [state_out_a, state_out_b]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_optional_repetition(self):
        edge_a = Edge('a', 'state_a')
        edge_b = Edge('b', 'state_b')
        state_a = State('state_a')
        state_b = State('state_b')

        edge_out_a = Edge('a', 'state_a')
        edge_out_a_e = Edge('', 'state_a')
        edge_out_b = Edge('b', 'state_b')
        edge_out_b_e = Edge('', 'state_b')
        state_out_a = State('state_a')
        state_out_b = State('state_b')

        in_edges = [edge_a, edge_b]
        new_end_states = [state_a, state_b]
        new_states = [state_a, state_b]
        repetition = None
        is_optional = True

        in_edges_out = [edge_out_a, edge_out_b, edge_out_a_e, edge_out_b_e]
        new_end_states_out = [state_out_a, state_out_b]
        new_states_out = [state_out_a, state_out_b]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_N_repetition(self):
        edge_a = Edge('a', 'state_a')
        edge_b = Edge('b', 'state_b')
        state_a = State('state_a')
        state_b = State('state_b')

        edge_out_a = Edge('a', 'state_a')
        edge_out_b = Edge('b', 'state_b')
        edge_out_a_2 = Edge('a', 'state_a_2')
        edge_out_b_2 = Edge('b', 'state_b_2')
        state_out_a = State('state_a', [edge_out_a_2, edge_out_b_2])
        state_out_b = State('state_b', [edge_out_a_2, edge_out_b_2])
        state_out_a_2 = State('state_a_2')
        state_out_b_2 = State('state_b_2')

        in_edges = [edge_a, edge_b]
        new_end_states = [state_a, state_b]
        new_states = [state_a, state_b]
        repetition = (2, 2)
        is_optional = False

        in_edges_out = [edge_out_a, edge_out_b]
        new_end_states_out = [state_out_a_2, state_out_b_2]
        new_states_out = [state_out_a, state_out_b, state_out_a_2, state_out_b_2]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_range_repetition(self):
        edge_a = Edge('a', 'state_a')
        edge_b = Edge('b', 'state_b')
        state_a = State('state_a')
        state_b = State('state_b')

        edge_out_a = Edge('a', 'state_a')
        edge_out_b = Edge('b', 'state_b')
        edge_out_a_2 = Edge('a', 'state_a_2')
        edge_out_b_2 = Edge('b', 'state_b_2')
        edge_out_a_3 = Edge('a', 'state_a_3')
        edge_out_a_3_e = Edge('', 'state_a_3')
        edge_out_b_3 = Edge('b', 'state_b_3')
        edge_out_b_3_e = Edge('', 'state_b_3')
        state_out_a = State('state_a', [edge_out_a_2, edge_out_b_2])
        state_out_b = State('state_b', [edge_out_a_2, edge_out_b_2])
        state_out_a_2 = State('state_a_2', [edge_out_a_3, edge_out_b_3, edge_out_a_3_e, edge_out_b_3_e])
        state_out_b_2 = State('state_b_2', [edge_out_a_3, edge_out_b_3, edge_out_a_3_e, edge_out_b_3_e])
        state_out_a_3 = State('state_a_3')
        state_out_b_3 = State('state_b_3')

        in_edges = [edge_a, edge_b]
        new_end_states = [state_a, state_b]
        new_states = [state_a, state_b]
        repetition = (2, 3)
        is_optional = False

        in_edges_out = [edge_out_a, edge_out_b]
        new_end_states_out = [state_out_a_3, state_out_b_3]
        new_states_out = [state_out_a, state_out_b, state_out_a_2, state_out_b_2, state_out_a_3, state_out_b_3]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_1_range_repetition(self):
        edge_a = Edge('a', 'state_a')
        edge_b = Edge('b', 'state_b')
        state_a = State('state_a')
        state_b = State('state_b')

        edge_out_a = Edge('a', 'state_a')
        edge_out_b = Edge('b', 'state_b')
        edge_out_a_2 = Edge('a', 'state_a_2')
        edge_out_b_2 = Edge('b', 'state_b_2')
        edge_out_a_3 = Edge('a', 'state_a_3')
        edge_out_a_3_e = Edge('', 'state_a_3')
        edge_out_b_3 = Edge('b', 'state_b_3')
        edge_out_b_3_e = Edge('', 'state_b_3')
        state_out_a = State('state_a', [edge_out_a_2, edge_out_b_2, edge_out_a_3_e, edge_out_b_3_e])
        state_out_b = State('state_b', [edge_out_a_2, edge_out_b_2, edge_out_a_3_e, edge_out_b_3_e])
        state_out_a_2 = State('state_a_2', [edge_out_a_3, edge_out_b_3, edge_out_a_3_e, edge_out_b_3_e])
        state_out_b_2 = State('state_b_2', [edge_out_a_3, edge_out_b_3, edge_out_a_3_e, edge_out_b_3_e])
        state_out_a_3 = State('state_a_3')
        state_out_b_3 = State('state_b_3')

        in_edges = [edge_a, edge_b]
        new_end_states = [state_a, state_b]
        new_states = [state_a, state_b]
        repetition = (1, 3)
        is_optional = False

        in_edges_out = [edge_out_a, edge_out_b]
        new_end_states_out = [state_out_a_3, state_out_b_3]
        new_states_out = [state_out_a, state_out_b, state_out_a_2, state_out_b_2, state_out_a_3, state_out_b_3]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_N_minus_repetition(self):
        edge_a = Edge('a', 'state_a')
        edge_b = Edge('b', 'state_b')
        state_a = State('state_a')
        state_b = State('state_b')

        edge_out_a = Edge('a', 'state_a')
        edge_out_b = Edge('b', 'state_b')
        edge_out_a_2 = Edge('a', 'state_a_2')
        edge_out_b_2 = Edge('b', 'state_b_2')
        edge_out_a_3 = Edge('a', 'state_a_3')
        edge_out_a_3_e = Edge('', 'state_a_3')
        edge_out_b_3 = Edge('b', 'state_b_3')
        edge_out_b_3_e = Edge('', 'state_b_3')
        state_out_a = State('state_a', [edge_out_a_2, edge_out_b_2, edge_out_a_3_e, edge_out_b_3_e])
        state_out_b = State('state_b', [edge_out_a_2, edge_out_b_2, edge_out_a_3_e, edge_out_b_3_e])
        state_out_a_2 = State('state_a_2', [edge_out_a_3, edge_out_b_3, edge_out_a_3_e, edge_out_b_3_e])
        state_out_b_2 = State('state_b_2', [edge_out_a_3, edge_out_b_3, edge_out_a_3_e, edge_out_b_3_e])
        state_out_a_3 = State('state_a_3')
        state_out_b_3 = State('state_b_3')

        in_edges = [edge_a, edge_b]
        new_end_states = [state_a, state_b]
        new_states = [state_a, state_b]
        repetition = (0, 3)
        is_optional = False

        in_edges_out = [edge_out_a, edge_out_b, edge_out_a_3_e, edge_out_b_3_e]
        new_end_states_out = [state_out_a_3, state_out_b_3]
        new_states_out = [state_out_a, state_out_b, state_out_a_2, state_out_b_2, state_out_a_3, state_out_b_3]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_N_plus_repetition(self):
        edge_a = Edge('a', 'state_a')
        edge_b = Edge('b', 'state_b')
        state_a = State('state_a')
        state_b = State('state_b')

        edge_out_a = Edge('a', 'state_a')
        edge_out_b = Edge('b', 'state_b')
        edge_out_a_2 = Edge('a', 'state_a_2')
        edge_out_b_2 = Edge('b', 'state_b_2')
        edge_out_a_3 = Edge('a', 'state_a_3')
        edge_out_b_3 = Edge('b', 'state_b_3')
        state_out_a = State('state_a', [edge_out_a_2, edge_out_b_2])
        state_out_b = State('state_b', [edge_out_a_2, edge_out_b_2])
        state_out_a_2 = State('state_a_2', [edge_out_a_3, edge_out_b_3])
        state_out_b_2 = State('state_b_2', [edge_out_a_3, edge_out_b_3])
        state_out_a_3 = State('state_a_3', [edge_out_a_3, edge_out_b_3])
        state_out_b_3 = State('state_b_3', [edge_out_a_3, edge_out_b_3])

        in_edges = [edge_a, edge_b]
        new_end_states = [state_a, state_b]
        new_states = [state_a, state_b]
        repetition = (3, float('inf'))
        is_optional = False

        in_edges_out = [edge_out_a, edge_out_b]
        new_end_states_out = [state_out_a_3, state_out_b_3]
        new_states_out = [state_out_a, state_out_b, state_out_a_2, state_out_b_2, state_out_a_3, state_out_b_3]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))

    def test_any_repetition(self):
        edge_a = Edge('a', 'state_a')
        edge_b = Edge('b', 'state_b')
        state_a = State('state_a')
        state_b = State('state_b')

        edge_out_a = Edge('a', 'state_a')
        edge_out_a_e = Edge('', 'state_a')
        edge_out_b = Edge('b', 'state_b')
        edge_out_b_e = Edge('', 'state_b')
        state_out_a = State('state_a', [edge_out_a, edge_out_b])
        state_out_b = State('state_b', [edge_out_a, edge_out_b])

        in_edges = [edge_a, edge_b]
        new_end_states = [state_a, state_b]
        new_states = [state_a, state_b]
        repetition = (0, float('inf'))
        is_optional = False

        in_edges_out = [edge_out_a, edge_out_b, edge_out_a_e, edge_out_b_e]
        new_end_states_out = [state_out_a, state_out_b]
        new_states_out = [state_out_a, state_out_b]
        expected = [in_edges_out, new_end_states_out, new_states_out]
        actual = repetition_applicator.apply_repetition(in_edges, new_end_states, new_states, repetition, is_optional)

        logger.debug(f'Actual result:\nin_edges: {actual[0]}\nnew_end_states: {actual[1]}\nnew_states: {actual[2]}')
        logger.debug(f'start_edges')
        self.assertTrue(edges_equal(actual[0], expected[0]))
        logger.debug(f'end_states')
        self.assertTrue(states_equal(actual[1], expected[1]))
        logger.debug(f'states')
        self.assertTrue(states_equal(actual[2], expected[2]))
