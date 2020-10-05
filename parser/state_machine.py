import logging
import string as string_module

from collections import defaultdict

FINAL_STATE = "FINAL"
START_STATE = "START"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

CHARACTER_CATEGORIES = {
    'CHAR': {'CHAR contains literally everything, this is handled specially'},
    'ALPHA': {c for c in string_module.ascii_lowercase + string_module.ascii_uppercase},
    'DIGIT': {c for c in string_module.digits}
}

class Edge():

    def __init__(self, input, dest, is_character_class=False):
        self.input = input # string Accepted token by this edge.
        self.dest = dest # string State ID of the destination of this edge.
        self.is_character_class = is_character_class # Whether this edge represents a character class.

    def clone(self):
        return Edge(self.input, self.dest, self.is_character_class)

    def __str__(self):
        val = f'{{Edge'
        if self.is_character_class:
            val += ' (character class)'
        val += f' | input: "{self.input}", dest: {self.dest}}}'
        return val

    def __repr__(self):
        return self.__str__()

    def get_input_length(self):
        if not self.is_character_class:
            return len(self.input)
        else:
            return 1

    def character_matches_category(self, c):
        assert self.is_character_class, f'character_matches_category() was called on {self}, which is not a character_class edge!'
        if self.input == 'CHAR':
            return True
        if c in CHARACTER_CATEGORIES[self.input]:
            return True
        return False

# START_STATE and FINAL_STATE may not have is_automata set to True.
class State():
    def __init__(self, id_, edges=[], is_automata=False):
        self.id = id_
        if not isinstance(edges, list):
            edges = [edges]
        elif edges == None or len(edges) == 0:
            edges = []
        for edge in edges:
            assert isinstance(edge, Edge), f'State {id_} got edge {edge} that was not an instance of class Edge!'
        self.edges = edges
        assert isinstance(is_automata, bool), f'Got is_automata value of {is_automata}, which was not a boolean! Perhaps a second edge you forgot to put into a list?'
        self.is_automata = is_automata

    def __str__(self):
        val = f'{{State '
        if self.is_automata:
            val += '(sub-automata) '
        val += f'| {self.id}: {[str(edge) for edge in self.edges]}}}'
        return val

    def __repr__(self):
        return self.__str__()

    def clone(self):
        return State(self.id, [edge.clone() for edge in self.edges], self.is_automata)

    def add_edge(self, edge):
        assert isinstance(edge, Edge), f'State {id_} got edge {edge} that was not an instance of class Edge!'
        self.edges.append(edge)

# Holds information about calls to sub-automata. Start is inclusive, end is
# exclusive.
class StateRecord():
    # (state_id: int or str, start: int, end: int, nested_path=[StateRecord]
    def __init__(self, automata_id, state_id, start, end, nested_path=None):
        self.automata_id = automata_id
        self.id = state_id
        self.start = start
        self.end = end
        self.nested_path = nested_path

    def __str__(self):
        val = f'StateRecord[{self.automata_id}] | state_id: "{self.id}" [{self.start}:{self.end}]'
        if self.nested_path:
            val += f' - {self.nested_path}'
        return val


    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.id == other.id and self.start == other.start and self.end == other.end and self.nested_path == other.nested_path

# State machine implementation for modified ABNF parsing. Records which pieces
# of the input string matched where, and has only one starting and final state each.
# TODO: Probably turn this into a push-down automata, since it looks like we'll need it.
class StateMachine():

    def __init__(self, id_=0, states=[]):
        self.id = id_ # IDs ending with _\d+ are reserved.
        for state in states:
            assert isinstance(state, State), f'Got state {state} that was not an instance of class State!'
        self.state_map = {state.id: state for state in states}
        self.nested_automata = {} # {automata_id:int: automata:StateMachine}
        self.alternatives_map = {} # {start:int:  [(state: string, start:int, path: list: StateRecord)]
        self.used_state_pos_map = defaultdict(set) # {start: set: (state, str_pos)}.

    def __str__(self):
        return f'State Machine {self.id}: {self.state_map}'

    def __repr__(self):
        return self.__str__()

    def add_state(self, state):
        assert isinstance(state, State), f'Got state {state} that was not an instance of class State!'
        assert state.id not in self.state_map.keys(), f'Attempted to add state {state} that was already present in state machine {self.id}!'
        self.state_map[state.id] = state.edges

    def add_edge(self, state_id, edge):
        assert isinstance(edge, Edge), f'State {id_} got edge {edge} that was not an instance of class Edge!'
        assert state_id in self.state_map.keys(), f'Attempted to add edge for nonexistent state {state} in state machine {self.id}!'
        self.state_map[state.id].append(edge)

    def register_automata(self, automata):
        self.nested_automata[automata.id] = automata

    # Checks if the entire string is accepted by the machine. Should not be called
    # after accepts_partial.
    # Returns (found: bool, path: list(StateRecord)
    def accepts(self, string):
        return self._accepts(string, partial_match=False)[0:1]

    # Returns the first accepting state reached by this automata over the given
    # string, starting from the specified start location. Further calls to this
    # method with the same start location will return additional accepting states,
    # until there are no more to be found. Further calls with different starting
    # locations will start entirely new searches from those locations.
    # Returns (found: bool, path: list(StateRecord), end_pos: int)
    def accepts_partial(self, string, start=0):
        return self._accepts(string, start=start, partial_match=True)

    def reset(self):
        logger.debug('Resetting machine {self}')
        self.alternatives_map = {} # {start:int:  [(state: string, start:int, path: list: StateRecord)]
        self.used_state_pos_map = defaultdict(set) # {start: set: (state, str_pos)}.

    def debug(self, string):
        logger.debug(f'{self.id}: ' + string)

    # TODO: Decide if this should to a more strict DFS, to obviate the need to copy the path all over.
    # Returns (found_bool, path_state_record, end_pos)
    def _accepts(self, string, start=0, partial_match=False):
        self.debug(f'Checking if state machine {self.id} accepts "{string}", starting at char {start} ({string[start:]})". ({"Partial match" if partial_match else "Full match"})')

        if start in self.alternatives_map.keys():
            alternatives = self.alternatives_map[start]
        else:
            alternatives = [(START_STATE, start, [])]
            self.alternatives_map[start] = alternatives

        used_state_pos = self.used_state_pos_map[start]
        self.debug(f'used_state_pos: {used_state_pos}')

        while True:
            self.debug(f'alternatives: {[alt[0:2] for alt in alternatives]}')

            # Alternatives list is empty, nothing else to check!
            if len(alternatives) == 0:
                self.debug(f'Finished search, no accepting path found.')
                return False, None, -1

            # Grab an alternative to investigate.
            state_id, i, prev_path = alternatives.pop()
            state = self.state_map[state_id]

            # Mark this state as explored for this starting position, so that
            # we don't go into infinite loops.
            used_state_pos.add((state_id, i))

            # TODO: Look into making this properly DFS, so that we don't store
            # so many copies of the path and can restore the below code.
            # Remove path that we're no longer using, if we've backed up.
            # Strict >, since end is exclusive. It can be the same as start though,
            # which means we're up to a character but that path step did not process anything.
            # while prev_path and prev_path[-1].end > i:
            #     logger.debug(f'Popping path step {prev_path[-1]} from path.')
            #     prev_path.pop()
            # logger.debug(f'Evaluating alternative at state "{state_id}" ({state}), with path: {prev_path}')

            # Making a call to a nested machine
            if state.is_automata:
                assert state_id in self.nested_automata.keys(), f'Got state_id {state_id} that was not in nested_automata list {self.nested_automata.keys()}!'
                # Note that the automata can be called multiple times. Different starting locations are treated
                # entirely indepentently.
                self.debug(f'State {state_id} is an automata, calling it with start={i}')
                accepted, nested_path, match_end = self.nested_automata[state_id].accepts_partial(string, start=i)
                # nested_path = self.nested_automata[state_id].get_path(i)
                prev_path.append(StateRecord(self.id, state_id + '_internal', i, match_end, nested_path))
                if not accepted:
                    # If the nested automata doesn't have any way to accept part of the string,
                    # then we continue to skip investigating the edges coming out of it.
                    continue
                else:
                    # The subautomata may be able to accept more, so we have to try it until
                    # it returns a failure.
                    alternatives.append((state_id, match_end, prev_path))
                i = match_end


            for edge in state.edges:
                # Make a copy
                path = list(prev_path)
                input_length = edge.get_input_length()
                match_end = i + input_length
                self.debug(f'Evaluating edge: {edge}')

                if string_matches_edge_input(string, i, edge):
                    self.debug(f'Matched: "{string[i:match_end]}" at position {i} in "{string}"')

                    path_step = StateRecord(self.id, state_id, i, match_end)
                    self.debug(f'Appending path step {path_step} to path {path}.')
                    path.append(path_step)

                    destination_state_id = edge.dest
                    if (destination_state_id, match_end) not in used_state_pos:
                        state_pos_path_tuple = (destination_state_id, match_end, path)
                        self.debug(f'Appending {state_pos_path_tuple} (equivalent to {(edge.dest, string[i+input_length:])}) to alternatives {alternatives}.')
                        assert state_pos_path_tuple[0] in self.state_map.keys(), f'Attempted to append state_pos_path_tuple {state_pos_path_tuple} whose state was not in the state map {self.state_map.keys()} to alternatives list {alternatives}!'
                        alternatives.append(state_pos_path_tuple)
                    else:
                        self.debug(f'Edge/position pair was already used, skipping.')
                else:
                    self.debug(f'Edge did not match!')

            if state_id == FINAL_STATE and (partial_match or i == len(string)):
                self.debug(f'Found an accepting path up to char {i}: {prev_path}')
                return True, prev_path, i
                break
        return False, None, -1

def string_matches_edge_input(string, i, edge):
    if edge.input == '':
        return True
    elif edge.is_character_class:
        if i <= len(string) - 1 and edge.character_matches_category(string[i]):
            return True
    elif i <= len(string) - len(edge.input) and edge.input == string[i:i+len(edge.input)]:
        return True
    else:
        return False
