import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def assert_states_equal(states1, states2):
    logger.debug(f'Comparing states:\n{states1}\n{states2}')
    if not isinstance(states1, list):
        states1 = [states1]
    if not isinstance(states2, list):
        states2 = [states2]

    assert len(states1) == len(states2), f'State list lengths are not equal:\n{states1}\n{states2}'

    for i in range(len(states1)):
        state1 = states1[i]
        state2 = states2[i]
        equal = True

        assert state1.id == state2.id, f'States do not have equal IDs:\n{state1}\n{state2}'
        assert state1.is_automata == state2.is_automata, f'States do not have equal is_automata:\n{state1}\n{state2}'
        assert len(state1.edges) == len(state2.edges), f'States do not have equal edge list lengths:\n{state1}\n{state2}'

        for j in range(len(state1.edges)):
            edge1 = state1.edges[j]
            edge2 = state2.edges[j]
            assert edge1.input == edge2.input, f'States {state1.id} and {state2.id} have mismatching inputs for edges at index {j}:\n{edge1}\n{edge2}'
            assert edge1.dest == edge2.dest, f'States {state1.id} and {state2.id} have mismatching inputs for edges at index {j}:\n{edge1}\n{edge2}'
            assert edge1.is_character_class == edge2.is_character_class, f'States {state1.id} and {state2.id} have mismatching inputs for edges at index {j}:\n{edge1}\n{edge2}'

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

def assert_state_machines_equal(machine1, machine2):
    logger.debug(f'Comparing machines:\n{machine1}\n{machine2}')
    assert machine1.id == machine2.id, f'Machine IDs did not match for {machine1} and {machine2}!'

    sort_func = lambda state: state.id
    machine1_states = list(machine1.state_map.values())
    machine2_states = list(machine2.state_map.values())
    sorted_m1_states = sorted(machine1_states, key=sort_func)
    sorted_m2_states = sorted(machine2_states, key=sort_func)
    logger.debug(machine1_states)
    assert_states_equal(sorted_m1_states, sorted_m2_states)

    assert len(machine1.nested_automata) == len(machine2.nested_automata), f'Nested automata dictionary lengths not match for {machine1} and {machine2}!'
    if len(machine1.nested_automata) > 0:
        sort_func = lambda state_machine: state_machine.id
        machines1 = list(machine1.nested_automata.values())
        machines2 = list(machine2.nested_automata.values())
        sorted_m1 = sorted(machines1, key=sort_func)
        sorted_m2 = sorted(machines2, key=sort_func)

        for i in range(len(sorted_m1)):
            nested1 = sorted_m1[i]
            nested2 = sorted_m2[i]
            assert_state_machines_equal(nested1, nested2), f'Nested automata {nested1} and {nested2} did not match for {machine1} and {machine2}!'
