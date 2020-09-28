import logging
import random
import re
import math
from collections import defaultdict

import state_clause_handler
import choices_util
import subtable_calls
import range_replacements

class Tag():

    def __init__(self, num, symbol):
        self.num = num
        self.symbol = symbol

    def __str__(self):
        return self.symbol

    def __repr__(self):
        return self.__str__()

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

    def gen_choice_recursive(self, choices_dict, choice_to_expand):
        if '$' not in choice_to_expand:
            # There were no tags in which to make replacements, so we need to do it now before extracting state data.
            # choice_to_expand = state_clause_handler.replace_state_interpolation(choice_to_expand, None, self.state)
            choice_to_expand = self.make_replacements(choice_to_expand, None)
            logging.debug(f'replaced choice_to_expand after no tags found, level {self.level}: {choice_to_expand}')
            choice_to_expand = self.extract_state(choice_to_expand)
            logging.debug(f'State: {self.state}')
            return choice_to_expand

        choice_to_expand, tags = prepare_tags(choice_to_expand)

        # Initial replacement to handle any interpolated values inbetween the start of the choice and the
        # first tag.
        logging.debug(f'initial pre-state interpolation at level {self.level} choice_to_expand: {choice_to_expand}')
        choice_to_expand = state_clause_handler.replace_state_interpolation(choice_to_expand, None, self.state)
        logging.debug(f'initial pre-state replacements at level {self.level} choice_to_expand: {choice_to_expand}')
        choice_to_expand = self.make_replacements(choice_to_expand, None)
        logging.debug(f'initial choice_to_expand, entering tags: {choice_to_expand}')

        for tag in tags:
            if tag.symbol not in choice_to_expand:
                # Something has removed this choice, probably a bracket deletion from a null choice.
                continue
            # logging.info(f'state: {self.state}')
            # logging.debug(f'choice_to_expand, level {self.level}: {choice_to_expand}')
            filtered_choice_list = self.filter_choices_dict(tag.num, choices_dict)
            # logging.debug(f'filtered_choice_list, level {self.level}: {filtered_choice_list}')
            choice_for_tag = self.pick_choice(filtered_choice_list, choice_to_expand, tag)
            logging.debug(f'weighed_choice, level {self.level}: {choice_for_tag}')
            # choice_for_tag.choice = self.make_replacements(choice_for_tag.choice)
            # logging.debug(f'replaced weighed_choice, level {self.level}: {choice_for_tag}')

            if self.level == self.params['uniqueness_level']:
                self.used_choices.append(choice_for_tag)
                self.remove_childless_parents(choice_to_expand, choice_for_tag)
            elif not choices_dict[choice_for_tag] and self.params['uniqueness_level'] == -1:
                # If there's nothing in the corresponding list, we're at a leaf node
                # and are done generating this choice, so uniqueness_level -1 applies.
                logging.info(f'appending choice_for_tag {choice_for_tag} to used_choices!')
                self.used_choices.append(choice_for_tag)
                self.remove_childless_parents(choice_to_expand, choice_for_tag)

            self.dict_and_choice_backtrace.append((choices_dict, choice_for_tag))
            self.level += 1
            recursed_choice = self.gen_choice_recursive(choices_dict[choice_for_tag], choice_for_tag.choice)
            logging.debug(f'recursed_choice, level {self.level}: {recursed_choice}')
            self.dict_and_choice_backtrace.pop()
            self.level -= 1

            # Now that we have all of our state updated from the recursive call,
            # we can use that information to replace any state interpolations
            # present between this substitution symbol and the next, or remove
            # their associated text if they have not been set.
            # tag_loc = choice_to_expand.find('$')
            # logging.debug(f'choice_to_expand, pre-state interpolation, level {self.level}: {choice_to_expand}')
            # logging.debug(f'Doing state interpolation for tag {tag.symbol} on {choice_to_expand}"')
            # choice_to_expand = state_clause_handler.replace_state_interpolation(choice_to_expand, tag, self.state)
            # logging.debug(f'Doing replacements for tag {tag.symbol} on {choice_to_expand}"')
            choice_to_expand = self.make_replacements(choice_to_expand, tag)

            # Symbols of the form $[N] allow manual overriding of the recursion ordering.
            # This makes it possible to choose a state-determining value before making
            # a choice that requires that state.
            # manual_ordering_override = '$[' + str(tag) + ']'
            # if choice_to_expand.find(manual_ordering_override) != -1:
            # logging.debug(f'choice_to_expand, pre-tag replacement, level {self.level}: {choice_to_expand}')
            # logging.debug(f'Replacing tag {tag.symbol} on {choice_to_expand}"')
            choice_to_expand = choice_to_expand.replace(tag.symbol, recursed_choice, 1)
            # else:
                # choice_to_expand = choice_to_expand.replace('$', recursed_choice, 1)

            # logging.debug(f'choice_to_expand, level {self.level}: {choice_to_expand}\n\n')

        # choice_to_expand = self.make_replacements(choice_to_expand, tag)
        # logging.debug(f'replaced choice_to_expand, level {self.level}: {choice_to_expand}')
        choice_to_expand = self.extract_state(choice_to_expand)
        # logging.debug(f'State: {self.state}')
        # logging.info(f'used_choices: {self.used_choices}')
        return choice_to_expand

    def filter_choices_dict(self, tag_num, choices_dict):
        filtered_choices = []
        for choice in choices_dict:
            if choice.tag_num != tag_num:
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
        state_pattern = re.compile(state_clause_handler.STATE_REGEXES['omni_state_modification'])
        match = state_pattern.search(generated_choice)
        while match:
            clause = generated_choice[match.start():match.end()]
            state, value = state_clause_handler.evaluate_state_modification(clause, self.state)
            self.state[state] = value

            generated_choice = generated_choice[:match.start()] + generated_choice[match.end():]

            match = state_pattern.search(generated_choice)
        return generated_choice
    #
    # def merge_state(self, state):
    #     for key, value in state.items():
    #         # logging.info(f'Writing to state: {key}, {value}.')
    #         self.state[key] = value

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
    def remove_childless_parents(self, choice_to_expand, removed_weighted_choice):
        for dict, weighted_choice in self.dict_and_choice_backtrace[::-1]:
            # logging.info(f'Removed {removed_weighted_choice}, going after its childless parents while creating level {self.level} choice {choice_to_expand}. wc: {weighted_choice}, dict: {choices_util.recursive_dict_print(dict)} used_choices: {self.used_choices}')
            tag_filtered_choices = [wc for wc in dict[weighted_choice].keys() if wc.tag_num == removed_weighted_choice.tag_num]
            # logging.info(f'tfc: {tag_filtered_choices}')
            unused_tag_filtered_choices = list(filter(lambda d: d not in self.used_choices, tag_filtered_choices))
            if len(unused_tag_filtered_choices) != 0:
                # logging.info(f'not all choices in {unused_tag_filtered_choices} were used, breaking!')
                break
            # logging.info(f'Adding {weighted_choice} to the used_choices list!')
            self.used_choices.append(weighted_choice)
            removed_weighted_choice = weighted_choice

    def make_replacements(self, choice_to_expand, tag):
        logging.debug(f'Making replacements on {choice_to_expand} for tag {tag}.')
        choice_to_expand, state = range_replacements.replace_ranges(choice_to_expand, tag, self.state)
        choice_to_expand = state_clause_handler.replace_state_interpolation(choice_to_expand, None, self.state)
        choice_to_expand, state = subtable_calls.make_subtable_calls(self.parent, choice_to_expand, tag, self.state)
        # choice_to_expand = self.make_subtable_calls(choice_to_expand, tag)
        logging.debug(f'Finished making replacements: {choice_to_expand} for tag {tag}.')

        return choice_to_expand

    # def replace_ranges(self, choice_to_expand, tag):
    #     logging.debug(f'Replacing ranges on {choice_to_expand} for tag {tag}.')
    #     num_replace = re.compile('\[(\d+)-(\d+)(G|N)?(%[a-zA-Z]\w+%)?\]')
    #     start = 0
    #     if tag:
    #         start = choice_to_expand.find(tag.symbol)
    #     match = choices_util.get_next_match(choice_to_expand, num_replace, start)
    #     # match = num_replace.search(choice_to_expand)
    #     logging.debug(f'Got match {match}, with updated start {start}.')
    #     while match:
    #         logging.debug(f'Replacing range {match.group(0)}')
    #         full_match = match.group(0)
    #         start = int(match.group(1))
    #         end = int(match.group(2))
    #         type = match.group(3)
    #         to_store = match.group(4)
    #
    #         val = None
    #         if type == 'N':
    #             # start = mean, end = stddev
    #             val = math.floor(random.gauss(start, end))
    #         elif type == 'G':
    #             #start = alpha, end = beta
    #             val = math.floor(random.gammavariate(start, end))
    #         else:
    #             val = random.randint(start, end)
    #
    #         logging.debug(f'Found range {full_match} for choice_to_expand {choice_to_expand}.')
    #         if match.end() < len(choice_to_expand) and choice_to_expand[match.end()] == '%':
    #             state_clause_start = match.end()
    #             state_clause_end = choice_to_expand.find('%', state_clause_start+1)
    #             raw_clause = choice_to_expand[state_clause_start+1:state_clause_end]
    #             for clause in state_clause_handler.clause_list_from_raw_clause(raw_clause):
    #                 logging.debug(f'Doing state calculation for clause {clause} in raw_clause {raw_clause}, with target {full_match}.')
    #                 val = state_clause_handler.evaluate_value_modification(clause, val, self.state)
    #             choice_to_expand = choice_to_expand[:state_clause_start] + choice_to_expand[state_clause_end+1:]
    #
    #         self.state[to_store] = val
    #
    #         choice_to_expand = choice_to_expand.replace(full_match, str(val))
    #         # match = num_replace.search(choice_to_expand)
    #         match = choices_util.get_next_match(choice_to_expand, num_replace, start)
    #     logging.debug(f'Finished replacing ranges on {choice_to_expand} for tag {tag}.')
    #     return choice_to_expand
    #
    # def make_subtable_calls(self, choice_to_expand, tag):
    #     subtable_replace = re.compile('@([a-zA-Z_]+)(\[(\d+)(-\d+)?, ?(-?\d+)\])?')
    #     start = 0
    #     if tag:
    #         start = choice_to_expand.find(tag.symbol)
    #     match = choices_util.get_next_match(choice_to_expand, subtable_replace, start)
    #     match = subtable_replace.search(choice_to_expand)
    #     while match:
    #         full_match = match.group(0)
    #         subtable_id = match.group(1)
    #         base_num_to_gen = match.group(3)
    #         end_num_to_gen = match.group(4)
    #         uniqueness_level = match.group(5)
    #
    #         # If both of these are filled out, we have a variable-length subtable call
    #         if base_num_to_gen != None and end_num_to_gen != None:
    #             end_num_to_gen = end_num_to_gen[1:]
    #             num_to_gen = random.randint(int(base_num_to_gen), int(end_num_to_gen))
    #         elif base_num_to_gen == None:
    #             num_to_gen = 1
    #         else:
    #             num_to_gen = int(base_num_to_gen)
    #
    #         if uniqueness_level == None:
    #             uniqueness_level = 0
    #         else:
    #             uniqueness_level = int(uniqueness_level)
    #
    #         logging.info(f'making call to subtable {subtable_id} with num_to_gen={num_to_gen} and uniqueness_level={uniqueness_level}.')
    #
    #         params = {'num':num_to_gen, 'uniqueness_level':uniqueness_level}
    #         subtable_choices, state = self.parent.call_subtable(subtable_id, params)
    #         self.merge_state(state)
    #
    #         choice_to_expand, open, close = choices_util.handle_brace_enclosure(match.start(), choice_to_expand, delete_all=False)
    #         # choice_to_expand = process_brace_clause(choice_to_expand, '@' + subtable_id, delete=False)
    #         choice_to_expand = choice_to_expand.replace(full_match, subtable_choices[0], 1)
    #         choice_to_expand = replace_repeated_subtable_clauses(choice_to_expand, subtable_choices, subtable_id)
    #         # Since the other clauses could be anywhere, we just back up to the beginning again.
    #         start = 0
    #         if tag:
    #             start = choice_to_expand.find(tag.symbol)
    #
    #         # match = subtable_replace.search(choice_to_expand)
    #         match = choices_util.get_next_match(choice_to_expand, subtable_replace, start)
    #     return choice_to_expand

    def pick_choice(self, filtered_choices, choice_to_expand, tag):
        clause_modded_weights_by_uuid = {wc.uuid: self.get_clause_modded_weight(wc) for wc in filtered_choices}
        total_weight = sum(clause_modded_weights_by_uuid.values())
        assert total_weight > 0, f'Total weight was <= 0, most likely you wrote a generation that removed all valid choices from a config. Choices given were: {filtered_choices}, at level {self.level}, with used_choices of {self.used_choices}, tag: {tag}, choice_to_expand: {choice_to_expand}'
        rand = random.randint(1, total_weight)

        for wc in filtered_choices:
            rand -= clause_modded_weights_by_uuid[wc.uuid]
            if rand <= 0:
                return wc
        raise ValueError(f'Failed to select a choice when provided {filtered_choices}.')

    def get_clause_modded_weight(self, wc):
        if not wc.clause_list:
            return wc.weight
        clause_modded_weight = wc.weight
        for clause in wc.clause_list:
            clause_modded_weight = state_clause_handler.evaluate_value_modification(clause, clause_modded_weight, self.state)
        return clause_modded_weight

def prepare_tags(choice_to_expand):
    num_tags = choice_to_expand.count('$')
    tags = []
    for i in range(1, num_tags+1):
        symbol = f'$[{i}]'
        tags.append(Tag(i, symbol))
        if symbol not in choice_to_expand:
            match = re.search('\$(?!\[\d+\])', choice_to_expand)
            choice_to_expand = choice_to_expand[:match.start()] + symbol + choice_to_expand[match.start()+1:]
    return choice_to_expand, tags

# def replace_repeated_subtable_clauses(choice_to_expand, subtable_choices, subtable_id):
#     logging.debug(f'subtable generated values: {subtable_choices}')
#     # Matches using results beyond the first are of the form '@\dsubtable_id'.
#     i = 2
#     for choice in subtable_choices[1:]:
#         # Add two, because we start counting at 1, and have already used
#         # one value above.
#         numbered_id = '@' + str(i) + subtable_id
#         id_index = choice_to_expand.index(numbered_id)
#         logging.debug(f'subtable numbered_id: {numbered_id}')
#         choice_to_expand, _, _ = choices_util.handle_brace_enclosure(id_index, choice_to_expand, delete_all=False)
#         # choice_to_expand = process_brace_clause(choice_to_expand, numbered_id, delete=False)
#         choice_to_expand = choice_to_expand.replace(numbered_id, choice, 1)
#         i += 1
#
#     numbered_id = '@' + str(i) + subtable_id
#     id_index = choice_to_expand.index(numbered_id)
#     while numbered_id in choice_to_expand:
#         logging.debug(f'Removing subtable clause, numbered_id: {numbered_id}')
#         choice_to_expand, _, _ = choices_util.handle_brace_enclosure(id_index, choice_to_expand, delete_all=True)
#         # choice_to_expand = process_brace_clause(choice_to_expand, numbered_id, delete=True)
#         i += 1
#         numbered_id = '@' + str(i) + subtable_id
#     return choice_to_expand

# def process_brace_clause(generated_choice, numbered_id, delete=False):
#     choice_loc = generated_choice.index(numbered_id)
#     try:
#         first_brace = generated_choice.rindex('{', 0, choice_loc)
#         last_brace = generated_choice.index('}', choice_loc)
#     except ValueError:
#         logging.info(f'no braces found for numbered_id "{numbered_id}" in choice "{generated_choice}".')
#         return generated_choice
#     if delete:
#         # Delete everything inside the braces.
#         result = generated_choice[:first_brace] + generated_choice[last_brace+1:]
#     else:
#         # Remove the braces.
#         result = generated_choice[:first_brace] + generated_choice[first_brace+1:last_brace] + generated_choice[last_brace+1:]
#
#     logging.debug(f'choice after processing braces: {result}')
#     return result


# if __name__ == '__main__':
#     set_up_logging.set_up_logging()
#
#     print()