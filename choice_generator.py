import logging
import random
import re
import math
from collections import defaultdict

import state_clause_handler

import nested_choices

# Generates a random choice.
class ChoiceGenerator():

    def __init__(self, nested_choices):
        self.parent = nested_choices
        self.level = -1
        self.generated_choice = ''
        self.dict_and_choice_backtrace = []
        self.used_choices = []
        self.state = defaultdict(int)
        self.params = {'num': 1, 'uniqueness_level': 0, 'uniqueness_mode':'each'}
        self.data = {}

    def gen_choice(self, choices_dict, params):
        generated_choice = '$'
        self.level = 1
        self.dict_and_choice_backtrace = []
        self.params = params

        generated_choice = self.gen_choice_recursive(choices_dict, generated_choice)
        logging.info(f'generated_choice: {generated_choice}')

        return generated_choice, self.state

    def gen_choice_recursive(self, choices_dict, generated_choice):
        if '$' not in generated_choice:
            return generated_choice

        tags = list(range(1, generated_choice.count('$') + 1))

        for tag in tags:
            logging.info(f'state: {self.state}')
            logging.debug(f'generated_choice, level {self.level}: {generated_choice}')
            filtered_choice_list = self.filter_choices_dict(tag, choices_dict)
            logging.debug(f'filtered_choice_list, level {self.level}: {filtered_choice_list}')
            weighted_choice = self.pick_choice(filtered_choice_list)
            logging.debug(f'weighed_choice, level {self.level}: {weighted_choice}')
            weighted_choice.choice = self.make_replacements(weighted_choice.choice)
            logging.debug(f'replaced weighed_choice, level {self.level}: {weighted_choice}')

            if self.level == self.params['uniqueness_level']:
                self.used_choices.append(weighted_choice)
                self.remove_childless_parents()

            # If there's nothing in the corresponding list, we're at a leaf node
            # and are done generating this choice.
            if not choices_dict[weighted_choice]:
                if self.params['uniqueness_level'] == -1:
                    self.used_choices.append(weighted_choice)
                    self.remove_childless_parents()

            self.dict_and_choice_backtrace.append((choices_dict, weighted_choice))
            self.level += 1
            recursed_choice = self.gen_choice_recursive(choices_dict[weighted_choice], weighted_choice.choice)
            logging.debug(f'recursed_choice, level {self.level}: {recursed_choice}')
            self.dict_and_choice_backtrace.pop()
            self.level -= 1

            # Symbols of the form $[N] allow manual overriding of the recursion ordering.
            # This makes it possible to choose a state-determining value before making
            # a choice that requires that state.
            manual_ordering_override = '$[' + str(tag) + ']'
            if generated_choice.find(manual_ordering_override) != -1:
                generated_choice = generated_choice.replace(manual_ordering_override, recursed_choice, 1)
            else:
                generated_choice = generated_choice.replace('$', recursed_choice, 1)

            generated_choice = self.extract_state(generated_choice)
            logging.debug(f'generated_choice, level {self.level}: {generated_choice}\n\n')

        return generated_choice

    def filter_choices_dict(self, tag, choices_dict):
        filtered_choices = []
        for choice in choices_dict:
            if choice.tag != tag:
                continue
            if choice in self.used_choices:
                continue
            if not self.passes_state_check(choice):
                continue
            filtered_choices.append(choice)
        return filtered_choices

    def passes_state_check(self, choice):
        return True

    # generated_choice: A choice generated during the recursion process which
    # is fully generated. (i.e. has no more '$' in it.)
    def extract_state(self, generated_choice):
        start = generated_choice.find(' %')
        end = generated_choice.find('%', start+2) # +2 because len(' %') == 2
        while start != -1:
            clause = generated_choice[start:end+1]
            logging.info(f'start: {start}, end: {end}, clause "{clause}" in choice "{generated_choice}"')
            state, value = state_clause_handler.evaluate_state_modification(clause, self.state)
            logging.info(f'state: {state}, value: {value}')
            self.state[state] = value

            generated_choice = generated_choice[:start] + generated_choice[end+1:]

            start = generated_choice.find(' %', end+1)
            end = generated_choice.find('%', start+2) # +2 because len(' %') == 2
        return generated_choice

    def merge_state(self, state):
        for key, value in state.items():
            # logging.info(f'Writing to state: {key}, {value}.')
            self.state[key] = value

    # This one's a bit tricky. We take a backtrace object which contains a trail of WCs
    # that we may have to remove, and the dictionaries that they occur in. Starting from the
    # bottom up, we look up the values under each WC in its parent dictionary, which lets us
    # check if there are any left uncovered. If there are, then we break. Otherwise, we will
    # use the dictionary to remove the WC, and go up another level to check again.
    #
    # self.dict_and_choice_backtrace: Dict, keys are WeightedChoice objects, and values
    # are nested dicts of the same form. The only keys that aren't dicts with WC keys
    # are empty dicts.
    #
    # self.used_choices: List of WeightedChoice objects.
    def remove_childless_parents(self):
        for dict, weighted_choice in self.dict_and_choice_backtrace[::-1]:
            tag_filtered_choices = [wc for wc in dict[weighted_choice].keys() if wc.tag == weighted_choice.tag]
            if len(list(filter(lambda d: d not in self.used_choices, tag_filtered_choices))) != 0:
                break
            self.used_choices.append(weighted_choice)

    def make_replacements(self, generated_choice):
        generated_choice = self.replace_ranges(generated_choice)
        generated_choice = self.make_subtable_calls(generated_choice)

        return generated_choice

    def replace_ranges(self, generated_choice):
        num_replace = re.compile('\[(\d+)-(\d+)(G|N)?\]')
        match = num_replace.search(generated_choice)
        while match:
            full_match = match.group(0)
            start = int(match.group(1))
            end = int(match.group(2))
            type = match.group(3)

            val = None
            if type == 'N':
                # start = mean, end = stddev
                val = math.floor(random.gauss(start, end))
            elif type == 'G':
                #start = alpha, end = beta
                val = math.floor(random.gammavariate(start, end))
            else:
                val = random.randint(start, end)

            logging.info(f'match {full_match} for generated choice {generated_choice} with match.end() = {match.end()}')
            if match.end() < len(generated_choice) and generated_choice[match.end()] == '%':
                state_clause_start = match.end()
                state_clause_end = generated_choice.find('%', state_clause_start+1)
                clause = generated_choice[state_clause_start:state_clause_end+1]
                logging.debug(f'Doing state calculation for clause {clause}, with target {full_match}.')
                logging.info(f'val_pre: {val}')
                val = state_clause_handler.evaluate_value_modification(clause, val, self.state)
                logging.info(f'val_post: {val}')
                generated_choice = generated_choice[:state_clause_start] + generated_choice[state_clause_end+1:]

            generated_choice = generated_choice.replace(full_match, str(val))
            match = num_replace.search(generated_choice)
        return generated_choice

    def make_subtable_calls(self, generated_choice):
        subtable_replace = re.compile('@([a-zA-Z_]+)(\[(\d+)(-\d+)?, ?(-?\d+)\])?')
        match = subtable_replace.search(generated_choice)
        while match:
            full_match = match.group(0)
            subtable_id = match.group(1)
            base_num_to_gen = match.group(3)
            end_num_to_gen = match.group(4)
            uniqueness_level = match.group(5)
            logging.debug(f'full_match: {full_match}')

            # If both of these are filled out, we have a variable-length subtable call
            if base_num_to_gen != None and end_num_to_gen != None:
                end_num_to_gen = end_num_to_gen[1:]
                logging.debug('Generating random length subtable call.')
                logging.debug(f'base_num_to_gen: {base_num_to_gen}')
                logging.debug(f'end_num_to_gen: {end_num_to_gen}')
                num_to_gen = random.randint(int(base_num_to_gen), int(end_num_to_gen))
            elif base_num_to_gen == None:
                num_to_gen = 1
            else:
                num_to_gen = int(base_num_to_gen)

            if uniqueness_level == None:
                uniqueness_level = 0
            else:
                uniqueness_level = int(uniqueness_level)

            logging.info(f'making call to subtable {subtable_id} with num_to_gen={num_to_gen} and uniqueness_level={uniqueness_level}.')

            params = {'num':num_to_gen, 'uniqueness_level':uniqueness_level}
            subtable_choices, state = self.parent.call_subtable(subtable_id, params)
            self.merge_state(state)

            generated_choice = process_brace_clause(generated_choice, '@' + subtable_id, delete=False)
            generated_choice = generated_choice.replace(full_match, subtable_choices[0], 1)
            generated_choice = replace_repeated_subtable_clauses(generated_choice, subtable_choices, subtable_id)

            match = subtable_replace.search(generated_choice)
        return generated_choice

    def pick_choice(self, filtered_choices):
        clause_modded_weights_by_uuid = {wc.uuid: self.get_clause_modded_weight(wc) for wc in filtered_choices}
        logging.info(f'CMC: {clause_modded_weights_by_uuid}')
        total_weight = sum(clause_modded_weights_by_uuid.values())
        assert total_weight > 0, f'Total weight was <= 0, most likely you wrote a generation that removed all valid choices from a config. Choices given were: {filtered_choices}'
        rand = random.randint(1, total_weight)

        for wc in filtered_choices:
            logging.info(f'rand: {rand}|wc: {wc}')
            rand -= clause_modded_weights_by_uuid[wc.uuid]
            if rand <= 0:
                return wc
        raise ValueError(f'Failed to select a choice when provided {filtered_choices}.')

    def get_clause_modded_weight(self, wc):
        if wc.clause == None:
            return wc.weight
        clause_modded_weight = state_clause_handler.evaluate_value_modification(wc.clause, wc.weight, self.state)
        return clause_modded_weight

def replace_repeated_subtable_clauses(generated_choice, subtable_choices, subtable_id):
    logging.debug(f'subtable generated values: {subtable_choices}')
    # Matches using results beyond the first are of the form '@\dsubtable_id'.
    i = 2
    for choice in subtable_choices[1:]:
        # Add two, because we start counting at 1, and have already used
        # one value above.
        numbered_id = '@' + str(i) + subtable_id
        logging.debug(f'subtable numbered_id: {numbered_id}')
        generated_choice = process_brace_clause(generated_choice, numbered_id, delete=False)
        generated_choice = generated_choice.replace(numbered_id, choice, 1)
        i += 1

    numbered_id = '@' + str(i) + subtable_id
    while numbered_id in generated_choice:
        logging.debug(f'Removing subtable clause, numbered_id: {numbered_id}')
        generated_choice = process_brace_clause(generated_choice, numbered_id, delete=True)
        i += 1
        numbered_id = '@' + str(i) + subtable_id
    return generated_choice

def process_brace_clause(generated_choice, numbered_id, delete=False):
    choice_loc = generated_choice.index(numbered_id)
    try:
        first_brace = generated_choice.rindex('{', 0, choice_loc)
        last_brace = generated_choice.index('}', choice_loc)
    except ValueError:
        logging.info(f'no braces found for numbered_id "{numbered_id}" in choice "{generated_choice}".')
        return generated_choice
    if delete:
        # Delete everything inside the braces.
        result = generated_choice[:first_brace] + generated_choice[last_brace+1:]
    else:
        # Remove the braces.
        result = generated_choice[:first_brace] + generated_choice[first_brace+1:last_brace] + generated_choice[last_brace+1:]

    logging.debug(f'choice after processing braces: {result}')
    return result
