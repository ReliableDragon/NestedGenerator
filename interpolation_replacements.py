import re
import logging

import choices_util
import state_clause_handler
from state_regexes import STATE_REGEXES

def replace_state_interpolation(to_replace, tag, state):
    logging.debug(f'Beginning state interpolation for tag {tag} over "{to_replace}".')
    pattern = re.compile(STATE_REGEXES['omni_state_interpolation']) # TODO: Conditional interpolation
    start = 0
    if tag:
        start = to_replace.find(tag.symbol)+len(tag.symbol)

    while True:
        match = choices_util.get_next_match(to_replace, pattern, start)

        if match == None:
            logging.debug('no match!')
            break
        if inside_rng(match, to_replace):
            logging.debug('inside rng!')
            start = match.end()
            continue
        # Conditional interpolation
        clause = to_replace[match.start():match.end()]
        logging.debug(f'match {match.group(0)} found, proceeding to interpolate {to_replace}')
        interpolation = state_clause_handler.evaluate_state_interpolation(clause, state)
        logging.debug(f'Interpolation came back with "{interpolation}".')

        delete_bracket_clause = True
        if interpolation != None:
            to_replace = to_replace.replace(clause, str(interpolation))
            delete_bracket_clause = False
            to_replace, open, close = choices_util.handle_brace_enclosure(match.start(), to_replace, False)
            if open != None and close != None:
                start -= sum([brace < start for brace in [open, close]])
        else:
            to_replace, open, close = choices_util.handle_brace_enclosure(match.start(), to_replace, True)
            if open != None and close != None:
                # Back up however far the string has been modified before start.
                start = choices_util.backup_for_deletion(start, open, close)
            else:
                logging.info(f'Interpolation returned None, but no enclosing braces were found while processing {to_replace}. Removing just {to_replace[match.start():match.end()]}')
                to_replace = to_replace[:match.start()] + to_replace[match.end():]
                # Back up however far the string has been modified before start.
                start = choices_util.backup_for_deletion(start, match.start(), match.end())

        logging.debug(f'State interpolation for tag {tag} on "{to_replace}" finished')
    return to_replace

def inside_rng(match, to_replace):
    enclosing_braces = choices_util.get_enclosing_braces(match.start(), to_replace, '[', ']')
    return enclosing_braces != (None, None)
