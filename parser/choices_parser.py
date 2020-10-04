import logging
import re
import uuid

import elements_splitter
from state_machine import Edge, State, StateMachine, START_STATE, FINAL_STATE, CHARACTER_CATEGORIES

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ParseTree():

    def __init__(self, id_):
        self.id = id_

def parse_from_string(choice_string):
    lines = choice_string.split('\n')

    # Drop empty lines and comments
    lines = [line.strip().split(';')[0] for line in lines if line.strip()]

    machines = {} # {automata_id:string: automata:StateMachine}
    submachines_needed = {} # {automata_id:string: [automata_id:string]}

    for line in lines:
        rulename, elements = line.split('=', 1)
        rulename = rulename.strip()
        machine, submachines_needed = parse_elements(rulename, elements)
        machines[machine.id] = machine
        submachines_needed[machine.id] = submachines_needed

# Returns machine: StateMachine
def parse_elements(rulename, elements):
    machine = StateMachine(rulename)
    machine_start = State(START_STATE)
    machine_end = State(FINAL_STATE)

    elements = elements_splitter.split_into_tokens(elements)
    start_edges, end_states, states = recursive_parse_elements(elements)

    for state in states:
        machine.add_state(state)
    for start_edge in start_edges:
        machine_start.add_edge(start_edge)
    for end_state in end_states:
        machine_end.add_edge('', state.id)

    machine.add_state(machine_start)
    machine.add_state(machine_end)

    return machine

# Returns start_edges: [Edge], end_states: [State], states: [State]
def recursive_parse_elements(elements, used_state_ids=None):
    logger.debug('Parsing elements {elements}')
    current_states = []
    next_states = []
    start_edges = []
    end_states = []
    states = []
    if used_state_ids == None:
        used_state_ids = {} # {state_id:string: times_used:int}
    first_iteration = True

    i = 0
    while i < len(elements):
        logger.debug(f'i: {i} | {elements[i:]}')
        tokens, i = get_concurrent_tokens(elements, i)
        logger.debug(f'Tokens: {tokens}')

        for token in tokens:
            logger.debug(f'Processing token "{token}"')
            token, repetition = get_repetition(token)
            logger.debug(f'Got repetition. token: "{token}", repetition: {repetition}')
            token, is_optional = get_optionality(token)
            logger.debug(f'Got optionality. token: "{token}", is_optional: {is_optional}')

            # If we have a group, we have to recurse down into it, because the internal
            # structure of these states could be anything.
            if isinstance(token, list):
                logger.debug(f'Token "{token}" is list, recursing.')
                # TODO: Fix repetition with recursive calls. Probably just make an
                # apply_repetition method that works on the values returned here and
                # either skips them if they're optional or duplicates the states and
                # wires up edges between copies, including a loop from the end to the
                # start of the last copy if it's infinite. We'll have to go from the
                # states copied from end_states_recursed and use start_edges_recursed
                # to determine where the edges should go, but I think it shouldn't be
                # too bad. We might just be able to straight up copy start_edges_recursed
                # and add suffixes, but it's too late for me to be 100% positive.
                start_edges_recursed, end_states_recursed, recursed_states = recursive_parse_elements(token, used_state_ids)

                if first_iteration:
                    start_edges += start_edges_recursed
                else:
                    for current_state in current_states:
                        for edge in start_edges_recursed:
                            current_state.add_edge(edge)

                states += recursed_states
                next_states += end_states_recursed

            else:
                token, is_automata = is_automata_token(token)

                # Make sure the token hasn't been used before. If it has, then we
                # need to add a suffix onto it.
                # TODO: Make sure state machines know to ignore this suffix, or find
                # a better way to register which state machine goes with which token.
                if token in used_state_ids:
                    unique_token = token + f'_#{used_state_ids[token]+1}'
                    logger.debug(f'Token "{token}" is already in use. Changing to {unique_token}.')
                    used_state_ids[token] += 1
                    # token = new_token
                else:
                    unique_token = token
                    used_state_ids[token] = 1

                new_state = State(unique_token, is_automata = is_automata)

                in_edge = Edge(token, new_state.id)
                if first_iteration:
                    logger.debug(f'Appending edge {in_edge} start_edges.')
                    start_edges.append(in_edge)
                else:
                    logger.debug(f'Appending edge {in_edge} current_states.')
                    for current_state in current_states:
                        current_state.add_edge(in_edge)

                repeated_states = apply_repetition(in_edge, new_state, repetition)
                logger.debug(f'Got repeated_states {repeated_states}.')

                if is_optional or (repetition and repetition[0] == 0):
                    logger.debug(f'Current state is optional.')
                    skip_edge = Edge('', repeated_states[-1].id)
                    if first_iteration:
                        logger.debug(f'Added skip edge {skip_edge} to start_edges.')
                        start_edges.append(skip_edge)
                    else:
                        logger.debug(f'Adding skip edge {skip_edge} to current_states.')
                        for current_state in current_states:
                            current_state.add_edge(skip_edge)

                states += repeated_states
                next_states.append(repeated_states[-1])
                logger.debug(f'states: {states}, next_states: {next_states}')
            # End if isinstance(token, list) else clause
        # End for token in tokens loop
        first_iteration = False
        logger.debug(f'Reached end of concurrent tokens, setting current_states to next_states.')
        current_states = next_states
        next_states = []
    # End i < len(elements) loop
    end_states = current_states

    logger.debug(f'Returning {(start_edges, end_states, states)}.')
    return start_edges, end_states, states

def is_automata_token(token):
    is_character_class = token in CHARACTER_CATEGORIES.keys()
    quoted_string = False
    if is_quoted_string(token):
        quoted_string = True
        token = dequote_string(token)
    is_automata = not quoted_string and not is_character_class
    return token, is_automata

def get_concurrent_tokens(elements, i):
    concurrent_elements = []
    concurrent_elements.append(elements[i])
    while i+1 < len(elements) and elements[i+1] == '/':
        assert i+2 < len(elements), f'Got a "/" with nothing following it in "{elements}"!'
        i += 2
        concurrent_elements.append(elements[i])
    i += 1
    return concurrent_elements, i

def get_repetition(element):
    if not isinstance(element, list):
        return element, None
    min_reps = 0
    max_reps = float('inf')
    match = re.fullmatch('(\d*)?\*(\d*)|(\d+)?', element[0])
    if match:
        if match.group(1):
            min_reps = int(match.group(1))
        if match.group(2):
            max_reps = int(match.group(2))
        if match.group(3):
            min_reps = max_reps = int(match.group(3))
        return element[1], (min_reps, max_reps)
    else:
        return element, None

def get_optionality(element):
    if not isinstance(element, list):
        return element, False
    if element[0] == '[' and element[-1] == ']':
        unbracketed_element = element[1:-1]
        if len(unbracketed_element) == 1:
            unbracketed_element = unbracketed_element[0]
        return unbracketed_element, True
    else:
        return element, False

# Retuns [repeated_states]
def apply_repetition(edge, state, repetition):
    if repetition == None or repetition[1] == 1:
        return [state]

    states = [state]
    state_id = state.id
    min_reps, max_reps = repetition
    logger.debug(f'Applying repetition of {min_reps}-{max_reps} to state {state_id}')

    states_to_create = max_reps
    if max_reps == float('inf'):
        logger.debug(f'max_reps is inf, creating min_reps states instead and adding self-loop on last state.')
        states_to_create = min_reps

    for i in range(2, states_to_create+1):
        n_state_id = f'{state_id}_{i}'
        logger.debug(f'Creating state {n_state_id}')

        next_state = State(n_state_id, is_automata = state.is_automata)
        next_edge = edge.clone()
        next_edge.dest = next_state.id

        states[-1].add_edge(next_edge)
        logger.debug(f'Appended edge {next_edge} to state {states[-1].id}')
        states.append(next_state)
        logger.debug(f'Appended state {next_state}')

    logger.debug(f'States: {[state.id for state in states]}')

    if max_reps == float('inf'):
        self_loop_edge = edge.clone()
        self_loop_edge.dest = states[-1].id
        logging.debug(f'Adding self-arc to last state, {self_loop_edge.dest}.')
        states[-1].add_edge(self_loop_edge)
    else:
        # Subtract 1, because min_reps is 1 indexed, but our array is 0 indexed.
        min_state_index_to_skip = max(0, min_reps-1)
        # Technically this is the first index to exclude, since the right side is exclusive.
        max_state_index_to_skip = max_reps - 1
        for i in range(min_state_index_to_skip, max_state_index_to_skip):
            logging.debug(f'Adding skip arc from state {i} ({states[i].id}) to final state ({states[-1].id})')
            states[i].add_edge(Edge('', states[-1].id))

    return states

def is_quoted_string(string):
    return string[0] == '"' and string[-1] == '"'

def dequote_string(string):
    return string[1:-1]

# if __name__ == '__main__':
#     args = set_up_logging.set_up_logging()
