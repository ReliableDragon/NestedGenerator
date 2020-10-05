import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
