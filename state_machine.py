import logging
import set_up_logging

FINAL_STATE = "FINAL"
START_STATE = "START"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Edge():

    def __init__(self, input, dest):
        self.input = input
        self.dest = dest

    def __str__(self):
        return f'{{input: "{self.input}", dest: {self.dest}}}'

    def __repr__(self):
        return self.__str__()


class State():

    def __init__(self, id_, edges=[]):
        self.id = id_
        if not isinstance(edges, list):
            edges = [edges]
        for edge in edges:
            assert isinstance(edge, Edge), f'State {id_} got edge {edge} that was not an instance of class Edge!'
        self.edges = edges

    def __str__(self):
        return f'State {self.id}: {[str(edge) for edge in self.edges]}'

    def __repr__(self):
        return self.__str__()


# State machine implementation for modified ABNF parsing. Records which pieces
# of the input string matched where, and has only one starting and final state each.
# TODO: Probably turn this into a push-down automata, since it looks like we'll need it.
class StateMachine():

    def __init__(self, id_=0, states=[]):
        self.id = id_
        for state in states:
            assert isinstance(state, State), f'Got edge {state} that was not an instance of class Edge!'
        self.state_map = {state.id: state.edges for state in states}
        self.parsed_value = ""
        self.sub_values = {}
        self.stack = []

    def __str__(self):
        return f'State Machine {self.id}: {self.state_map}'

    def __repr__(self):
        return self.__str__()

    def add_state(self, state):
        self.state_map[state.id] = state
        if final:
            self.final_states.append(state)

    def accepts(self, string):
        logger.debug(f'Checking if machine {self} accepts "{string}".')
        used_state_pos = [] # Of the form (state, str_pos).
        alternatives = [(START_STATE, 0)]

        while True:
            logger.debug(f'alternatives: {alternatives}')

            if len(alternatives) == 0:
                logger.debug(f'Finished search, no accepting path found.')
                return False

            state, i = alternatives.pop()
            used_state_pos.append((state, i))
            logger.debug(f'state id: {state}, edges: {self.state_map[state]}')

            for edge in self.state_map[state]:
                input_length = len(edge.input)
                logger.debug(f'edge: {edge}')

                # if not edge.input:
                #     state_pos_pair = (edge.dest, i)
                #     if state_pos_pair not in used_choices:
                #         logger.debug(f'Appending {state_pos_pair} (equivalent to {(edge.dest, string[i+input_length:])})')
                #         append_if_not_used(state_pos_pair, alternatives, used_values)
                #     else:
                #         logger.debug(f'Edge/position pair was already used, skipping.')
                #     append_if_not_used((edge.dest, i), alternatives, used_values)
                if string_matches_edge_input(string, i, edge):
                    logger.debug(f'Matched: "{string[i:i+input_length]}"')
                    state_pos_pair = (edge.dest, i+input_length)
                    if state_pos_pair not in used_state_pos:
                        logger.debug(f'Appending {state_pos_pair} (equivalent to {(edge.dest, string[i+input_length:])})')
                        alternatives.append(state_pos_pair)
                    else:
                        logger.debug(f'Edge/position pair was already used, skipping.')

            if state == FINAL_STATE and i == len(string):
                logger.debug(f'Found an accepting path.')
                return True
                break
        return False

def string_matches_edge_input(string, i, edge):
    return edge.input == '' or (i <= len(string) - len(edge.input) and edge.input == string[i:i+len(edge.input)])

def append_if_not_used(value, target, used_choices):
    if value not in used_choices:
        target.append(value)

if __name__ == '__main__':
    args = set_up_logging.set_up_logging()
