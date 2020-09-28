import logging
import math
import re

import clause_calculator
import set_up_logging
import choices_util

from collections import defaultdict

CALCULATION_CLAUSE_RE = '([\^\-\+/\*\(\)0-9\w]+|"[\w ]+")'
COMPARATOR_RE = '([=<>!]{1,2})'
STATE_RE = '([a-zA-Z]\w+)'
EFFECT_RE = '([\^\-\+/\*]=|=)'
CONDITION_RE = f'{CALCULATION_CLAUSE_RE}{COMPARATOR_RE}{CALCULATION_CLAUSE_RE}'
STATE_MOD_EFFECT_RE = f'{STATE_RE}:{EFFECT_RE}{CALCULATION_CLAUSE_RE}'

VALID_COMPARISONS = ['==', '>=', '>', '<=', '<', '!=']
STATE_REGEXES = {
    'value_modification': f'%{EFFECT_RE}{CALCULATION_CLAUSE_RE}%',
    'conditional_value_modification': f'%{CONDITION_RE}->{EFFECT_RE}{CALCULATION_CLAUSE_RE}%',
    'state_modification': f' %{STATE_MOD_EFFECT_RE}%',
    'conditional_state_modification': f' %{CONDITION_RE}->{STATE_MOD_EFFECT_RE}%',
    'omni_state_modification': f' %({CONDITION_RE}->)?{STATE_MOD_EFFECT_RE}%',
    'state_interpolation': f'%{STATE_RE}%',
    'conditional_state_interpolation': f'%{CONDITION_RE}->{STATE_RE}%',
}

class StateClauseHandler():

    def __init__(self):
        self.condition = None
        self.lhs = None
        self.comparator = None
        self.rhs = None
        self.target_state = None
        self.target =  None
        self.effect = None
        self.magnitude = None
        self.type = None
        self.is_condition_valid = False

    def process_conditional_value_modification(self, match):
        logging.info('beginning process_conditional_value_modification')
        self.type = 'conditional_value_modification'
        self.lhs = match.group(1)
        self.comparator = match.group(2)
        self.rhs = match.group(3)
        self.effect = match.group(4)
        self.magnitude = match.group(5)

        self.calculate_lhs()
        self.calculate_rhs()
        self.calculate_magnitude()

        logging.info('doing comparison')
        if self.do_comparison():
            return self.calculate_modification()
        else:
            return self.target

    def process_value_modification(self, match):
        self.type = 'value_modification'
        self.effect = match.group(1)
        self.magnitude = match.group(2)
        self.is_condition_valid = True

        self.calculate_magnitude()

        return self.calculate_modification()

    def process_conditional_state_modification(self, match):
        self.type = 'conditional_state_modification'
        self.lhs = match.group(1)
        self.comparator = match.group(2)
        self.rhs = match.group(3)
        self.target_state = match.group(4)
        self.target = self.state[self.target_state]
        self.effect = match.group(5)
        self.magnitude = match.group(6)

        self.calculate_lhs()
        self.calculate_rhs()
        self.calculate_magnitude()

        if self.do_comparison():
            return self.calculate_modification()
        else:
            return self.target

    def process_state_modification(self, match):
        self.type = 'state_modification'
        self.target_state = match.group(1)
        self.target = self.state[self.target_state]
        self.effect = match.group(2)
        self.magnitude = match.group(3)
        self.is_condition_valid = True

        self.calculate_magnitude()

        return self.calculate_modification()

    def do_comparison(self):
        assert self.type in ['conditional_state_modification', 'conditional_value_modification']
        assert self.comparator in VALID_COMPARISONS

        logging.info(f'comparing with lhs={self.lhs}, comparator={self.comparator}, rhs={self.rhs}')
        if self.comparator == '==':
            self.is_condition_valid = (self.lhs == self.rhs)
        elif self.comparator == '>':
            self.is_condition_valid = (self.lhs > self.rhs)
        elif self.comparator == '<=':
            self.is_condition_valid = (self.lhs <= self.rhs)
        elif self.comparator == '<':
            self.is_condition_valid = (self.lhs < self.rhs)
        elif self.comparator == '<=':
            self.is_condition_valid = (self.lhs <= self.rhs)
        elif self.comparator == '!=':
            self.is_condition_valid = (self.lhs != self.rhs)

        logging.info(f'comparison result was {self.is_condition_valid}')
        return self.is_condition_valid

    def calculate_modification(self):
        value = None
        if self.effect == '*=':
            value = self.target * self.magnitude
        elif self.effect == '+=':
            value = self.target + self.magnitude
        elif self.effect == '-=':
            value = self.target - self.magnitude
        elif self.effect == '/=':
            value = self.target / self.magnitude
        elif self.effect == '^=':
            value = self.target ** self.magnitude
        elif self.effect == '=':
            value = self.magnitude

        return value

    def calculate_magnitude(self):
        value = clause_calculator.calculate(self.magnitude, self.state)
        self.magnitude = value
        return value

    def calculate_rhs(self):
        value = clause_calculator.calculate(self.rhs, self.state)
        self.rhs = value
        return value

    def calculate_lhs(self):
        value = clause_calculator.calculate(self.lhs, self.state)
        self.lhs = value
        return value

def evaluate_value_modification(condition, target, state):
    handler = StateClauseHandler()
    handler.condition = condition
    handler.target = target
    handler.state = state
    handler.is_condition_valid = False
    value_modification = re.fullmatch(STATE_REGEXES['value_modification'], condition)
    conditional_value_modification = re.fullmatch(STATE_REGEXES['conditional_value_modification'], condition)

    if value_modification:
        # logging.info('got value_modification')
        return handler.process_value_modification(value_modification)
    elif conditional_value_modification:
        # logging.info('got conditional_value_modification')
        return handler.process_conditional_value_modification(conditional_value_modification)
    else:
        raise ValueError(f'condition "{condition}" passed to evaluate_value_modification was not of a value modification form!')

# def handle_state_effects(to_replace, tag_loc, state):
#     next_tag_loc = to_replace.find('$', tag_loc+1)
#     if next_tag_loc == -1: # was !=
#         next_tag_loc = len(to_replace)
#     to_replace = to_replace[tag_loc+1:]
#
#     start = to_replace.find('%', tag_log+1, next_tag_loc)
#     end = to_replace.find('%', start+1, next_tag_loc)
#
#     while start != -1:
#         assert end != -1, f'Found starting % but didn\'t find matching one in line {line} while processing location {tag_loc}.'
#         clause = to_replace[start:end+1]
#
#         if re.match(STATE_REGEXES['state_modification'], clause) or re.match(STATE_REGEXES['conditional_state_modification'], clause):
#             evaluate_state_modification(clause, state)
#         elif re.match(STATE_REGEXES['state_interpolation'], clause) or re.match(STATE_REGEXES['conditional_state_interpolation'], clause):
#             replace_state_interpolation(to_replace, clause, state)
#
#     start = to_replace.find('%', end+1, next_tag_loc)
#     end = to_replace.find('%', start+1, next_tag_loc)


def evaluate_state_modification(condition, state):
    handler = StateClauseHandler()
    handler.condition = condition
    handler.state = state
    handler.is_condition_valid = False
    state_modification = re.fullmatch(STATE_REGEXES['state_modification'], condition)
    conditional_state_modification = re.fullmatch(STATE_REGEXES['conditional_state_modification'], condition)

    if state_modification:
        # logging.info('got state_modification')
        value = handler.process_state_modification(state_modification)
        return handler.target_state, value
    elif conditional_state_modification:
        # logging.info('got conditional_state_modification')
        value = handler.process_conditional_state_modification(conditional_state_modification)
        return handler.target_state, value
    else:
        raise ValueError(f'condition "{condition}" passed to evaluate_state_modification was not of a state modification form!')

def clause_list_from_raw_clause(raw_clause):
    return ['%' + clause + '%' for clause in raw_clause.split('|')]

def replace_state_interpolation(to_replace, tag, state):
    # logging.debug(f'beginning state interpolation over {to_replace}')
    pattern = re.compile(STATE_REGEXES['state_interpolation'])
    start = 0
    if tag:
        start = to_replace.find(tag.symbol)
    # logging.debug(f'Starting from character {start}.')
    # logging.debug(f'narrowed range to {to_replace[start:]}')
    # next_tag_loc = to_replace.find('$', tag_loc+1)
    # if next_tag_loc == -1: # was !=
    #     next_tag_loc = len(to_replace)
    # start, end = find_endpoints_for_interpolation(to_replace, tag)
    # match = pattern.search(to_replace, start, end)
    # start = to_replace.find('%', 0, next_tag_loc)
    # end = to_replace.find('%', start+1, next_tag_loc)
    # first_loop = True
    while True:
        # first_loop = False
        match = choices_util.get_next_match(to_replace, pattern, start)
        if match == None:
            break
        enclosing_braces = choices_util.get_enclosing_braces(match.start(), to_replace, '[', ']')
        if enclosing_braces != (None, None):
            start = match.end()
            continue
        logging.debug(f'match {match.group(0)} found, proceeding to interpolate {to_replace}')
        clause = to_replace[match.start():match.end()]
        state_name = clause[1:-1]
        if state_name in state.keys():
            state_value = state[state_name]
            to_replace = to_replace.replace(clause, str(state_value))
            to_replace, open, close = choices_util.handle_brace_enclosure(match.start(), to_replace, False)
            if open != None and close != None:
                start -= sum([brace < start for brace in [open, close]])
        else:
            to_replace, open, close = choices_util.handle_brace_enclosure(match.start(), to_replace, True)
            if open != None and close != None:
            # logging.debug(f'state missing for {state_name}, removing it')
            # open, close = choices_util.get_enclosing_braces(match.start(), to_replace, '{', '}')
            # if any([open, close]):
            #     assert all([open, close]), f'Enclosing braces for clause {clause} in replacement string {to_replace} when processing tag {tag} were not both found. Returned locations were {open}, {close}.'
            #     logging.debug(f'braces found, removing everything in {to_replace[open:close+1]}')
            #     to_replace = to_replace[:open] + to_replace[close+1:]
                # Back up however far the string has been modified before start.
                start = choices_util.backup_for_deletion(start, open, close)
            else:
                logging.info(f'State {state_name} was unable to be interpolated, but no enclosing braces were found while processing {to_replace}. Removing just {to_replace[match.start():match.end()+1]}')
                to_replace = to_replace[:match.start()] + to_replace[match.end()+1:]
                # Back up however far the string has been modified before start.
                start = choices_util.backup_for_deletion(start, match.start(), match.end())
        # match = choices_util.get_next_match(to_replace, pattern, start)

    return to_replace

if __name__ == '__main__':
    set_up_logging.set_up_logging()

    for type, regex in STATE_REGEXES.items():
        logging.debug(f'{type} regex: {regex}')

    state = defaultdict(int, {'wealth': 10, 'money': 256, 'dogs': 1, 'cats': 3, 'fish': 12, 'name': 'Gabe'})
    print(evaluate_value_modification('%(10+wealth)*3>money-200->=dogs*(cats+fish)%', 100, state)) # 15
    print(evaluate_state_modification(' %(wealth+wealth/2*4)^2/2>money->cash:-=dogs*(cats+fish)%', state)) # -15
    print(evaluate_state_modification(' %(wealth+wealth/2*4)^2/2>-dogs->money:+=money-(dogs*252)%', state)) # 260
    print(evaluate_state_modification(' %name>"aaa"->whoami:=name%', state)) # 260
