import re
import logging

import choices_util
from state_regexes import STATE_REGEXES

def validate_choices(namespace_id, choices_string):
    assert len(choices_string) != 0, 'Got empty choices data!'
    lines = choices_string.split('\n')
    must_indent = False
    prev_indent = 0
    blank = False

    for line in lines:
        if line == '':
            if blank:
                raise Error(f'Found two blank lines in a row in {namespace_id}.')
            blank == True
            continue

        blank == False
        indent = len(line) - len(line.lstrip(' '))
        if must_indent:
            assert indent == prev_indent + 2, f'Line {line} in {namespace_id} did not indent, despite a symbol requiring indentation on the previous line.'
            must_indent = False
        else:
            assert indent % 2 == 0 and indent < prev_indent + 2, f'Line {line} in {namespace_id} in  has an improper number of spaces.'

        assert re.match(f' *(\d+|\$)', line), f'Line {line} in {namespace_id} failed to match the expected format.'

        if '$' in line and line != (' ' * indent) + '$':
            must_indent = True

        value_patterns = [STATE_REGEXES['value_modification'], STATE_REGEXES['conditional_value_modification']]
        state_patterns = [STATE_REGEXES['state_modification'], STATE_REGEXES['conditional_state_modification']]
        loc = 0
        # There are two kinds of state clauses, one of which consumes the space before the '%'
        # and one of which doesn't.  To avoid mistakenly parsing one as the other, we first
        # find a '%', then see if it's actually a ' %', and base our analysis off that.
        value_start = line.find('%')
        value_stop = line.find('%', value_start + 1)
        state_start = line.find(' %', value_start-1, value_start+1)
        clause = line[value_start:value_stop+1]
        state_clause = line[state_start:value_stop+1]
        while value_start != -1:
            # logging.debug(f'value_start: {value_start}, value_stop: {value_stop}, state_start: {state_start}')
            # logging.debug(f'clause: "{clause}"')
            # logging.debug(f'state_clause: "{state_clause}"')
            if all(choices_util.get_enclosing_braces(value_start, line, lbrace='[', rbrace=']')):
                # This is a random number storage state
                pass
            elif re.fullmatch(STATE_REGEXES['omni_state_interpolation'], clause):
                # This is a state interpolation
                pass
            elif re.fullmatch(STATE_REGEXES['tag_state'], clause):
                # This is a tag state
                pass
            elif state_clause != -1 and re.fullmatch(STATE_REGEXES['omni_state_modification'], state_clause):
                # This is a state modification
                # clause = line[state_start:value_stop+1]
                assert(any(map(lambda pattern: re.fullmatch(pattern, state_clause), state_patterns))), f'State modification clause "{state_clause}" in line "{line}" has a format that does not match any valid format for state clauses!'
            elif re.fullmatch(STATE_REGEXES['omni_value_modification'], clause):
                # This is a value modification
                assert(any(map(lambda pattern: re.fullmatch(pattern, clause), value_patterns))), f'Value modification clause "{clause}" in line "{line}" has a format that does not match any valid format for state clauses!'
            else:
                raise ValueError(f'State clause "{clause}" in line "{line}" has a format that does not match any valid format for state clauses!')

            value_start = line.find('%', value_stop + 1)
            value_stop = line.find('%', value_start + 1)
            state_start = line.find(' %', value_start-1, value_start+1)
            clause = line[value_start:value_stop+1]
            state_clause = line[state_start:value_stop+1]

        prev_indent = indent

    logging.debug('Validated choices.')
