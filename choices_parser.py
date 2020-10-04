import logging
import re
import uuid

import set_up_logging
import elements_splitter
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
        rulename, elements = line.split('=', 1)
        rulename = rulename.strip()
        parse_elements(rulename, elements)


def parse_elements(rulename, elements):
    machines = {}
    machine = StateMachine(rulename)
    start_state = State(START_STATE)
    current_state = start_state

    elements = elements_splitter.split_into_tokens(elements)
    for element in elements:
        state_id = uuid.uuid4()
        if is_quoted_string(element):
            text = dequote_string(element)
            current_state.add_edge(Edge(text, state_id))


def is_quoted_string(string):
    return string[0] == '"' and string[-1] == '"'

def dequote_string(string):
    return string[1:-1]

if __name__ == '__main__':
    args = set_up_logging.set_up_logging()
