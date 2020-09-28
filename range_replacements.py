import re
import logging
import random
import math

import choices_util
import state_clause_handler

def replace_ranges(choice_to_expand, tag, state):
    logging.debug(f'Replacing ranges on {choice_to_expand} for tag {tag}.')
    num_replace = re.compile('\[(\d+)-(\d+)(G|N)?(%[a-zA-Z]\w+%)?\]')
    start = 0
    if tag:
        start = choice_to_expand.find(tag.symbol)
    match = choices_util.get_next_match(choice_to_expand, num_replace, start)
    # match = num_replace.search(choice_to_expand)
    logging.debug(f'Got match {match}, with updated start {start}.')
    while match:
        logging.debug(f'Replacing range {match.group(0)}')
        full_match = match.group(0)
        start = int(match.group(1))
        end = int(match.group(2))
        type = match.group(3)
        to_store = match.group(4)

        val = None
        if type == 'N':
            # start = mean, end = stddev
            val = math.floor(random.gauss(start, end))
        elif type == 'G':
            #start = alpha, end = beta
            val = math.floor(random.gammavariate(start, end))
        else:
            val = random.randint(start, end)

        logging.debug(f'Found range {full_match} for choice_to_expand {choice_to_expand}.')
        if match.end() < len(choice_to_expand) and choice_to_expand[match.end()] == '%':
            state_clause_start = match.end()
            state_clause_end = choice_to_expand.find('%', state_clause_start+1)
            raw_clause = choice_to_expand[state_clause_start+1:state_clause_end]
            for clause in state_clause_handler.clause_list_from_raw_clause(raw_clause):
                logging.debug(f'Doing state calculation for clause {clause} in raw_clause {raw_clause}, with target {full_match}.')
                val = state_clause_handler.evaluate_value_modification(clause, val, state)
            choice_to_expand = choice_to_expand[:state_clause_start] + choice_to_expand[state_clause_end+1:]
            state[to_store] = val

        choice_to_expand = choice_to_expand.replace(full_match, str(val))
        # match = num_replace.search(choice_to_expand)
        match = choices_util.get_next_match(choice_to_expand, num_replace, start)
    logging.debug(f'Finished replacing ranges on {choice_to_expand} for tag {tag}.')
    return choice_to_expand, state