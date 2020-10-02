import unittest
import logging
import sys

from state_machine import StateMachine, State, Edge, START_STATE, FINAL_STATE

# logging.basicConfig(level=logging.DEBUG)

class SimpleMachinesTestCase(unittest.TestCase):

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
        self.assertTrue(machine.accepts('ab'))
        self.assertFalse(machine.accepts('b'))

    # For accepting repeated tokens
    def test_accepts_repeated_symbols(self):
        machine = StateMachine(states=[State(START_STATE, Edge('a', FINAL_STATE)), State(FINAL_STATE, Edge('', START_STATE))])
        self.assertTrue(machine.accepts('a'))
        self.assertTrue(machine.accepts('aa'))
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
        self.assertTrue(machine.accepts('aa'))
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
        self.assertFalse(machine.accepts('aa'))
        self.assertTrue(machine.accepts('aaa'))
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
        self.assertTrue(machine.accepts('aa'))
        self.assertTrue(machine.accepts('aaa'))
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
        self.assertTrue(machine.accepts('ac'))

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
