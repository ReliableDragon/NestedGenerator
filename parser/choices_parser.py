import logging
import re
import uuid

import elements_splitter
import repetition_applicator
from state_machine import Edge, State, StateMachine, START_STATE, FINAL_STATE, CHARACTER_CATEGORIES

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

CONTROL_TOKENS = {'REGISTER_SUBTABLE_CALL', 'UNREGISTER_SUBTABLE_CALLS', 'SUBCHOICES', 'ADD_SUBCHOICE', 'REMOVE_SUBCHOICE', 'ADD_INDENT', 'REMOVE_INDENT'}

def parse_grammar():
    with open('grammar.txt') as f:
        grammar = f.read()
    result = parse_from_string(grammar)
    logger.debug(result)

def parse_from_string(choice_string):
    lines = choice_string.split('\n')

    # Drop empty lines and comments
    lines = [line.strip().split(';')[0] for line in lines if line.strip()]

    machines = {} # {automata_id:string: automata:StateMachine}
    submachines_needed = {} # {automata_id:string: [automata_id:string]}
    top_level_machine = None

    for line in lines:
        if not line:
            continue
        logger.debug(f'Parsing line {line}.')
        try:
            rulename, elements = line.split('=', 1)
        except ValueError:
            logger.debug(f'Got line without an equals sign: {line}')
            raise
        rulename = rulename.strip()
        machine = parse_elements(rulename, elements)
        machines[machine.id] = machine
        if top_level_machine == None:
            top_level_machine = machine

    for machine in machines.values():
        registered_ids = set()
        for state in machine.state_map.values():
            if state.is_automata:
                state_id = strip_suffixes(state.id)
                if state_id not in registered_ids:
                    machine.register_automata(machines[state_id])
                    registered_ids.add(state_id)

    return top_level_machine

def strip_suffixes(state_id):
    match = re.search('(_#\d+)?(_\d+)?$', state_id)
    if match:
        return state_id[:match.start()]
    else:
        # I'm pretty sure that pattern always matches, but better safe than sorry.
        return state_id

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
        end_state.add_edge(Edge('', FINAL_STATE))

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

    current_end_states = []
    new_end_states = []
    new_token_end_states = []
    new_states = []
    current_in_edges = []

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
                in_edges, new_token_end_states, new_states = recursive_parse_elements(token, used_state_ids)

            else:
                token, is_automata = is_automata_token(token)
                logger.debug(f'is_automata: {is_automata}')

                # Make sure the token hasn't been used before. If it has, then we
                # need to add a suffix onto it.
                # TODO: Make sure state machines know to ignore this suffix, or find
                # a better way to register which state machine goes with which token.
                if token in used_state_ids:
                    unique_token = token + f'_#{used_state_ids[token]+1}'
                    logger.debug(f'Token "{token}" is already in use. Changing to {unique_token}.')
                    used_state_ids[token] += 1
                else:
                    unique_token = token
                    used_state_ids[token] = 1

                new_state = State(unique_token, is_automata = is_automata)
                new_token_end_states = [new_state]
                new_states = [new_state]


                in_edge = Edge(token, new_state.id)
                in_edges = [in_edge]


            in_edges, new_token_end_states, new_states = repetition_applicator.apply_repetition(in_edges, new_token_end_states, new_states, repetition, is_optional)
            logger.debug(f'Got apply_repetition result of:\n  in_edges: {in_edges}\n  new_token_end_states: {new_token_end_states}\n  new_states: {new_states}')

            if first_iteration:
                logger.debug(f'Appending edge(s) {in_edges} to start_edges.')
                start_edges += in_edges
            else:
                for current_state in current_end_states:
                    for edge in in_edges:
                        logger.debug(f'Appending edge(s) {edge} to current_end_states {current_end_states}.')
                        current_state.add_edge(edge)
            logger.debug(f'Dumping new states {[state.id for state in new_states]} into states.')
            states += new_states
            logger.debug(f'Dumping new end_states for token {token} ({new_token_end_states}) into new_end_states ({new_end_states}).')
            new_end_states += new_token_end_states
            new_token_end_states = []
        # End for token in tokens loop
        first_iteration = False
        logger.debug(f'Reached end of concurrent tokens, setting current_end_states to new_end_states ({[state.id for state in new_end_states]}).')
        current_end_states = new_end_states
        new_end_states = []
    # End i < len(elements) loop
    end_states = current_end_states

    logger.debug(f'Returning:\n  start_edges: {start_edges}\n  end_states: {end_states}\n  states:{states}')
    return start_edges, end_states, states

def is_automata_token(token):
    if token in CHARACTER_CATEGORIES.keys():
        return token, False
    if token in CONTROL_TOKENS:
        return token, False
    if is_quoted_string(token):
        token = dequote_string(token)
        return token, False
    return token, True

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

def is_quoted_string(string):
    return string[0] == '"' and string[-1] == '"'

def dequote_string(string):
    return string[1:-1]

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parse_grammar()
