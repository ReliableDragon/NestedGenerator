import unittest
import logging
import sys

from state_machine import StateMachine, StateRecord, State, Edge, START_STATE, FINAL_STATE

# logging.basicConfig(level=logging.DEBUG)

def gen_test_state_record(id_, start, end):
    return StateRecord(0, id_, start, end)

class SimpleMachinesTestCase(unittest.TestCase):

    def test_state_record_equality(self):
        state_record_1 = StateRecord('a', START_STATE, 0, 0)
        state_record_2 = StateRecord('a', START_STATE, 0, 0)

        self.assertEqual(state_record_1, state_record_2)

    # For accepting raw tokens
    def test_accepts_single_symbol(self):
        machine = StateMachine(states=[State(START_STATE, Edge('abc', FINAL_STATE)), State(FINAL_STATE)])
        self.assertTrue(machine.accepts('abc'))

    # For accepting [optional] tokens
    def test_accepts_repeated_symbols(self):
        machine = StateMachine(
                states=[
                        State(START_STATE, Edge('a', FINAL_STATE), Edge('a', 'b')),
                        State('b', Edge('b', FINAL_STATE)),
                        State(FINAL_STATE)])
        self.assertTrue(machine.accepts('a'))
        machine.reset()
        self.assertTrue(machine.accepts('ab'))
        machine.reset()
        self.assertFalse(machine.accepts('b'))

    # For accepting repeated tokens
    def test_accepts_repeated_symbols(self):
        machine = StateMachine(states=[State(START_STATE, Edge('a', FINAL_STATE)), State(FINAL_STATE, Edge('', START_STATE))])
        self.assertTrue(machine.accepts('a'))
        machine.reset()
        self.assertTrue(machine.accepts('aa'))
        machine.reset()
        self.assertTrue(machine.accepts('aaa'))

    # For accepting N repeated tokens
    def test_accepts_N_repeated_symbols(self):
        machine = StateMachine(
                states=[
                        State(START_STATE, Edge('a', 'a1')),
                        State('a1', Edge('a', FINAL_STATE)),
                        State(FINAL_STATE)
                ])
        self.assertFalse(machine.accepts('a'))
        machine.reset()
        self.assertTrue(machine.accepts('aa'))
        machine.reset()
        self.assertFalse(machine.accepts('aaa'))

    # For accepting N* repeated tokens
    def test_accepts_N_star_repeated_symbols(self):
        machine = StateMachine(
                states=[
                        State(START_STATE, Edge('a', 'a1')),
                        State('a1', Edge('a', 'a2')),
                        State('a2', [Edge('a', FINAL_STATE), Edge('a', 'a2')]),
                        State(FINAL_STATE),
                        ])
        self.assertFalse(machine.accepts('a'))
        machine.reset()
        self.assertFalse(machine.accepts('aa'))
        machine.reset()
        self.assertTrue(machine.accepts('aaa'))
        machine.reset()
        self.assertTrue(machine.accepts('aaaa'))

    # For accepting *N repeated tokens
    def test_accepts_star_N_repeated_symbols(self):
        machine = StateMachine(
                states=[
                        State(START_STATE, [Edge('a', 'a1'), Edge('a', FINAL_STATE)]),
                        State('a1', [Edge('a', 'a2'), Edge('a', FINAL_STATE)]),
                        State('a2', Edge('a', FINAL_STATE)),
                        State(FINAL_STATE)
                        ])
        self.assertTrue(machine.accepts('a'))
        machine.reset()
        self.assertTrue(machine.accepts('aa'))
        machine.reset()
        self.assertTrue(machine.accepts('aaa'))
        machine.reset()
        self.assertFalse(machine.accepts('aaaa'))

    # For accepting A / B tokens
    def test_accepts_both_optional_paths(self):
        machine = StateMachine(
                states=[
                        State(START_STATE, [Edge('a', 'b'), Edge('a', 'c')]),
                        State('b', Edge('b', FINAL_STATE)),
                        State('c', Edge('c', FINAL_STATE)),
                        State(FINAL_STATE)
                ])
        self.assertTrue(machine.accepts('ab'))
        machine.reset()
        self.assertTrue(machine.accepts('ac'))

class ContinuationTestCases(unittest.TestCase):
    # For allowing repeated calls to sub-automata
    def test_continuation_works(self):
        machine = StateMachine(states=[State(START_STATE, Edge('a', FINAL_STATE)), State(FINAL_STATE, Edge('', START_STATE))])
        state_record = gen_test_state_record(START_STATE, 0, 1)
        state_records = [state_record]
        result = (True, state_records, 1)
        self.assertEqual(machine.accepts_partial('aaa'), result)

        state_record = gen_test_state_record(START_STATE, 0, 1)
        end_record = gen_test_state_record(FINAL_STATE, 1, 1)
        state_record2 = gen_test_state_record(START_STATE, 1, 2)
        state_records = [state_record, end_record, state_record2]
        result = (True, state_records, 2)
        self.assertEqual(machine.accepts_partial('aaa'), result)

        state_record = gen_test_state_record(START_STATE, 0, 1)
        end_record = gen_test_state_record(FINAL_STATE, 1, 1)
        state_record2 = gen_test_state_record(START_STATE, 1, 2)
        end_record2 = gen_test_state_record(FINAL_STATE, 2, 2)
        state_record3 = gen_test_state_record(START_STATE, 2, 3)
        state_records = [state_record, end_record, state_record2, end_record2, state_record3]
        result = (True, state_records, 3)
        self.assertEqual(machine.accepts_partial('aaa'), result)

        self.assertEqual(machine.accepts_partial('aaa'), (False, None, -1))

    # For allowing repeated calls to sub-automata
    def test_continuation_with_full_automata_repetition(self):
        machine = StateMachine(states=[
                State(START_STATE, Edge('', 'a')),
                State('a', Edge('a', FINAL_STATE)),
                State(FINAL_STATE, Edge('', START_STATE))])
        start_record = gen_test_state_record(START_STATE, 0, 0)
        a_record = gen_test_state_record('a', 0, 1)
        state_records = [start_record, a_record]
        result = (True, state_records, 1)
        self.assertEqual(machine.accepts_partial('aab'), result)

        start_record = gen_test_state_record(START_STATE, 0, 0)
        a_record = gen_test_state_record('a', 0, 1)
        end_record = gen_test_state_record(FINAL_STATE, 1, 1)
        start_record_2 = gen_test_state_record(START_STATE, 1, 1)
        a_record_2 = gen_test_state_record('a', 1, 2)
        state_records = [start_record, a_record, end_record, start_record_2, a_record_2]
        result = (True, state_records, 2)
        self.assertEqual(machine.accepts_partial('aab'), result)

        self.assertEqual(machine.accepts_partial('aab'), (False, None, -1))

    # For allowing repeated calls to sub-automata
    def test_continuation_with_internal_repetition(self):
        machine = StateMachine(states=[
                State(START_STATE, Edge('', 'a')),
                State('a', [Edge('a', 'a'), Edge('', FINAL_STATE)]),
                State(FINAL_STATE)])
        start_record = gen_test_state_record(START_STATE, 0, 0)
        a_record = gen_test_state_record('a', 0, 0)
        state_records = [start_record, a_record]
        result = (True, state_records, 0)
        self.assertEqual(machine.accepts_partial('aab'), result)

        start_record = gen_test_state_record(START_STATE, 0, 0)
        a_record = gen_test_state_record('a', 0, 1)
        a_record_2 = gen_test_state_record('a', 1, 1)
        state_records = [start_record, a_record, a_record_2]
        result = (True, state_records, 1)
        self.assertEqual(machine.accepts_partial('aab'), result)

        start_record = gen_test_state_record(START_STATE, 0, 0)
        a_record = gen_test_state_record('a', 0, 1)
        a_record_2 = gen_test_state_record('a', 1, 2)
        a_record_3 = gen_test_state_record('a', 2, 2)
        state_records = [start_record, a_record, a_record_2, a_record_3]
        result = (True, state_records, 2)
        self.assertEqual(machine.accepts_partial('aab'), result)

        self.assertEqual(machine.accepts_partial('aab'), (False, None, -1))

    # For testing the ordering of edge traversal. Since traversal is via DFS,
    # the internal loop should be preferred over the outside loop. Looks very
    # similar to the previous test, but validates something different.
    def test_edge_traversal_order(self):
        machine = StateMachine(states=[
                State(START_STATE, Edge('', 'a')),
                State('a', [Edge('a', 'a'), Edge('', FINAL_STATE)]),
                State(FINAL_STATE)])
        start_record = gen_test_state_record(START_STATE, 0, 0)
        a_record = gen_test_state_record('a', 0, 0)
        end_record = gen_test_state_record(FINAL_STATE, 0, 0)
        state_records = [start_record, a_record]
        result = (True, state_records, 0)
        self.assertEqual(machine.accepts_partial('aab'), result)

        start_record = gen_test_state_record(START_STATE, 0, 0)
        a_record = gen_test_state_record('a', 0, 1)
        a_record_2 = gen_test_state_record('a', 1, 1)
        state_records = [start_record, a_record, a_record_2]
        result = (True, state_records, 1)
        self.assertEqual(machine.accepts_partial('aab'), result)

        start_record = gen_test_state_record(START_STATE, 0, 0)
        a_record = gen_test_state_record('a', 0, 1)
        a_record_2 = gen_test_state_record('a', 1, 2)
        a_record_3 = gen_test_state_record('a', 2, 2)
        state_records = [start_record, a_record, a_record_2, a_record_3]
        result = (True, state_records, 2)
        self.assertEqual(machine.accepts_partial('aab'), result)

        self.assertEqual(machine.accepts_partial('aab'), (False, None, -1))

class SubMachineTestCases(unittest.TestCase):
    # For ensuring that sub-automata register and run properly.
    def test_sub_machines(self):
        machine = StateMachine(id_='a', states=[
                State(START_STATE, Edge('', 'b')),
                State('b', Edge('a', FINAL_STATE), is_automata=True),
                State(FINAL_STATE, Edge('', START_STATE))
                ])
        submachine_b = StateMachine(id_='b', states=[
                State(START_STATE, Edge('b', FINAL_STATE)),
                State(FINAL_STATE, Edge('', START_STATE))
                ])
        machine.register_automata(submachine_b)

        state_record = StateRecord('a', START_STATE, 0, 0)
        nested_start_record = StateRecord('b', START_STATE, 0, 1)
        submachine_record = StateRecord('a', 'b_internal', 0, 1, [nested_start_record])
        b_record = StateRecord('a', 'b', 1, 2)
        state_records = [state_record, submachine_record, b_record]
        result = (True, state_records, 2)
        self.assertEqual(machine.accepts_partial('ba'), result)

    #For ensuring that sub-automata register and run properly.
    def test_double_nested_sub_machines(self):
        machine = StateMachine(id_='c', states=[
                State(START_STATE, Edge('', 'b')),
                State('b', Edge('c', FINAL_STATE), is_automata=True),
                State(FINAL_STATE)
                ])
        submachine_b = StateMachine(id_='b', states=[
                State(START_STATE, Edge('', 'a')),
                State('a', Edge('b', FINAL_STATE), is_automata=True),
                State(FINAL_STATE)
                ])
        submachine_a = StateMachine(id_='a', states=[
                State(START_STATE, Edge('a', FINAL_STATE)),
                State(FINAL_STATE)
                ])

        submachine_b.register_automata(submachine_a)
        machine.register_automata(submachine_b)

        start_record = StateRecord('c', START_STATE, 0, 0)
        b_start_record = StateRecord('b', START_STATE, 0, 0)
        a_record = StateRecord('a', START_STATE, 0, 1)
        b_machine_record = StateRecord('b', 'a_internal', 0, 1, [a_record])
        b_record = StateRecord('b', 'a', 1, 2)
        c_machine_record = StateRecord('c', 'b_internal', 0, 2, [b_start_record, b_machine_record, b_record])
        c_record = StateRecord('c', 'b', 2, 3)
        state_records = [start_record, c_machine_record, c_record]
        result = (True, state_records, 3)
        self.assertEqual(machine.accepts_partial('abc'), result)

class AStarBRepeatedStateMachineTestCase(unittest.TestCase):

    def setUp(self):
        # Build a machine for (a+b)*
        state_0 = State(START_STATE, [Edge('a', "a*"), Edge('', FINAL_STATE)])
        state_1 = State("a*", [Edge("a", "a*"), Edge("b", FINAL_STATE)])
        state_2 = State(FINAL_STATE, [Edge('', START_STATE)])
        self.machine = StateMachine(states=[state_0, state_1, state_2])

    def test_accepts_empty_string(self):
        self.assertTrue(self.machine.accepts(""))

    def test_does_not_accept_a(self):
        self.assertFalse(self.machine.accepts("a"))

    def test_does_not_accept_b(self):
        self.assertFalse(self.machine.accepts("b"))

    def test_does_not_accept_c(self):
        self.assertFalse(self.machine.accepts("c"))

    def test_accepts_ab(self):
        self.assertTrue(self.machine.accepts("ab"))

    def test_does_not_accept_ba(self):
        self.assertFalse(self.machine.accepts("ba"))

    def test_does_not_accept_abc(self):
        self.assertFalse(self.machine.accepts("abc"))

    def test_does_not_accept_aaa(self):
        self.assertFalse(self.machine.accepts("aaa"))

    def test_does_not_accept_bbb(self):
        self.assertFalse(self.machine.accepts("bbb"))

    def test_accepts_aaabaaab(self):
        self.assertTrue(self.machine.accepts("aaaaaaab"))

    def test_accepts_aaabaaab(self):
        self.assertTrue(self.machine.accepts("aaabaaab"))

    def test_does_not_accept_aaabbaaab(self):
        self.assertFalse(self.machine.accepts("aaabbaaab"))

class AorBCorDEFFiveTimesStateMachineTestCase(unittest.TestCase):

    def setUp(self):
        # Build a machine for 5("a" / "bc" / "def")
        gen_edges = lambda i: [Edge('a', f'a{i}'), Edge('bc', f'bc{i}'), Edge('def', f'def{i}')]
        states = [State(START_STATE, gen_edges(0))]
        for i in range(4):
            states += [
                State(f'a{i}', gen_edges(i+1)),
                State(f'bc{i}', gen_edges(i+1)),
                State(f'def{i}', gen_edges(i+1)),
            ]
        states += [
            State(f'a4', Edge('', FINAL_STATE)),
            State(f'bc4', Edge('', FINAL_STATE)),
            State(f'def4', Edge('', FINAL_STATE)),
            State(f'FINAL')
        ]
        self.machine = StateMachine(states=states)

    def test_does_not_accept_empty_string(self):
        self.assertFalse(self.machine.accepts(""))

    def test_does_not_accept_a(self):
        self.assertFalse(self.machine.accepts("a"))

    def test_does_not_accept_b(self):
        self.assertFalse(self.machine.accepts("b"))

    def test_does_not_accept_bc(self):
        self.assertFalse(self.machine.accepts("bc"))

    def test_does_not_accept_c(self):
        self.assertFalse(self.machine.accepts("c"))

    def test_does_not_accept_cd(self):
        self.assertFalse(self.machine.accepts("cd"))

    def test_does_not_accept_cde(self):
        self.assertFalse(self.machine.accepts("cde"))

    def test_accepts_abcdefabc(self):
        self.assertTrue(self.machine.accepts("abcdefabc"))

    def test_does_not_accept_aaaa(self):
        self.assertFalse(self.machine.accepts("aaaa"))

    def test_accepts_aaaaa(self):
        self.assertTrue(self.machine.accepts("aaaaa"))

    def test_does_not_accept_aaaaaa(self):
        self.assertFalse(self.machine.accepts("aaaaaa"))

    def test_does_not_accept_cdecdecdecde(self):
        self.assertFalse(self.machine.accepts("cdecdecdecde"))

    def test_accepts_cdecdecdecdecde(self):
        self.assertFalse(self.machine.accepts("cdecdecdecdecde"))

    def test_does_not_accept_cdecdecdecde(self):
        self.assertFalse(self.machine.accepts("cdecdecdecdecdecde"))

    def test_accepts_defabcaa(self):
        self.assertTrue(self.machine.accepts("defabcaa"))

if __name__ == '__main__':
    unittest.main()
