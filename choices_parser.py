import logging
import re
import uuid

import set_up_logging
from state_machine import Edge, State, StateMachine, START_STATE, FINAL_STATE

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ParseTree():

    def __init__(self, id_):
        self.id = id_

def parse_from_string(choice_string):
    lines = choice_string.split('\n')

    # Drop empty lines and comments
    lines = [line.strip().split(';')[0] for line in lines if line.strip()]

    for line in lines:
        rulename, elements = line.split('=')
        rulename = rulename.strip()
        parse_elements(rulename, elements)


def parse_elements(rulename, elements):
    machines = {}
    machine = StateMachine(rulename)
    start_state = State(START_STATE)
    current_state = start_state

    elements = split_into_parts(elements)
    elements = elements.split(' ').strip()
    state_id = uuid.uuid4()
    for element in elements:
        state_id = uuid.uuid4()
        if is_quoted_string(element):
            text = dequote_string(element)
            current_state.add_edge(Edge(text, state_id))

def split_into_parts(elements):
    logger.debug(f'Parsing elements "{elements}".')
    result = []
    quoted = False
    parens = 0
    token = ''
    i = -1
    # for i, c in enumerate(elements):
    while i < len(elements)-1:
        i += 1
        c = elements[i]
        logger.debug(f'Processing character "{c}", quoted = {quoted}, parens = {parens}, token = "{token}", result = {result}.')

        if c == ' ':
            if token:
                logger.debug(f'Adding token "{token}" to results.')
                result.append(token)
            token = ''
            continue

        token += c

        if c == '"':
            while len(token) == 1 or c != '"':
                i += 1
                c = elements[i]
                token += c

        if c == '(':
            parens += 1
            while parens > 0:
                i += 1
                c = elements[i]
                if c == '(':
                    parens += 1
                if c == ')':
                    parens -= 1
                token += c
            logger.debug(f'Processing parenthetized clause "{token}".')
            token = split_into_parts(token[1:-1])

    if token:
        result.append(token)
    logger.debug(f'Returning results "{result}".')

    return result

def is_quoted_string(string):
    return string[0] == '"' and string[-1] == '"'

def dequote_string(string):
    return string[1:-1]

if __name__ == '__main__':
    args = set_up_logging.set_up_logging()
