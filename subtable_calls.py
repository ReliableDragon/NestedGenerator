import re
import logging
import random
import choices_util

def make_subtable_calls(parent, choice_to_expand, tag, state):
    subtable_replace = re.compile('@([a-zA-Z_]+)(\[(\d+)(-\d+)?, ?(-?\d+)\])?')
    start = 0
    if tag:
        start = choice_to_expand.find(tag.symbol)
    match = choices_util.get_next_match(choice_to_expand, subtable_replace, start)
    match = subtable_replace.search(choice_to_expand)
    while match:
        full_match = match.group(0)
        subtable_id = match.group(1)
        base_num_to_gen = match.group(3)
        end_num_to_gen = match.group(4)
        uniqueness_level = match.group(5)

        # If both of these are filled out, we have a variable-length subtable call
        if base_num_to_gen != None and end_num_to_gen != None:
            end_num_to_gen = end_num_to_gen[1:]
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
        subtable_choices, new_state = parent.call_subtable(subtable_id, params)
        state = merge_state(state, new_state)

        choice_to_expand, open, close = choices_util.handle_brace_enclosure(match.start(), choice_to_expand, delete_all=False)
        # choice_to_expand = process_brace_clause(choice_to_expand, '@' + subtable_id, delete=False)
        choice_to_expand = choice_to_expand.replace(full_match, subtable_choices[0], 1)
        choice_to_expand = replace_repeated_subtable_clauses(choice_to_expand, subtable_choices, subtable_id)
        # Since the other clauses could be anywhere, we just back up to the beginning again.
        start = 0
        if tag:
            start = choice_to_expand.find(tag.symbol)

        # match = subtable_replace.search(choice_to_expand)
        match = choices_util.get_next_match(choice_to_expand, subtable_replace, start)
    return choice_to_expand, state

def replace_repeated_subtable_clauses(choice_to_expand, subtable_choices, subtable_id):
    logging.debug(f'subtable generated values: {subtable_choices}')
    # Matches using results beyond the first are of the form '@\dsubtable_id'.
    i = 2
    for choice in subtable_choices[1:]:
        # Add two, because we start counting at 1, and have already used
        # one value above.
        numbered_id = '@' + str(i) + subtable_id
        id_index = choice_to_expand.index(numbered_id)
        logging.debug(f'subtable numbered_id: {numbered_id}')
        choice_to_expand, _, _ = choices_util.handle_brace_enclosure(id_index, choice_to_expand, delete_all=False)
        # choice_to_expand = process_brace_clause(choice_to_expand, numbered_id, delete=False)
        choice_to_expand = choice_to_expand.replace(numbered_id, choice, 1)
        i += 1

    numbered_id = '@' + str(i) + subtable_id
    while numbered_id in choice_to_expand:
        id_index = choice_to_expand.index(numbered_id)
        logging.debug(f'Removing subtable clause, numbered_id: {numbered_id}')
        choice_to_expand, _, _ = choices_util.handle_brace_enclosure(id_index, choice_to_expand, delete_all=True)
        # choice_to_expand = process_brace_clause(choice_to_expand, numbered_id, delete=True)
        i += 1
        numbered_id = '@' + str(i) + subtable_id
    return choice_to_expand

def merge_state(state, new_state):
    for key, value in new_state.items():
        # logging.info(f'Writing to state: {key}, {value}.')
        state[key] = value
