import logging
import math
import re

import clause_calculator
import set_up_logging

from collections import defaultdict

CALCULATION_CLAUSE_RE = '([\^\-\+/\*\(\)0-9\w]+|"[\w ]+")'
COMPARATOR_RE = '([=<>!]{1,2})'
STATE_RE = '([a-zA-Z]\w+)'
EFFECT_RE = '([\^\-\+/\*]=|=)'

VALID_COMPARISONS = ['==', '>=', '>', '<=', '<', '!=']
STATE_REGEXES = {
    'value_modification': f'%{EFFECT_RE}{CALCULATION_CLAUSE_RE}%',
    'conditional_value_modification': f'%{CALCULATION_CLAUSE_RE}{COMPARATOR_RE}{CALCULATION_CLAUSE_RE}->{EFFECT_RE}{CALCULATION_CLAUSE_RE}%',
    'state_modification': f' %{STATE_RE}:{EFFECT_RE}{CALCULATION_CLAUSE_RE}%',
    'conditional_state_modification': f' %{CALCULATION_CLAUSE_RE}{COMPARATOR_RE}{CALCULATION_CLAUSE_RE}->{STATE_RE}:{EFFECT_RE}{CALCULATION_CLAUSE_RE}%',
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
        logging.debug(f'calculated magnitude value: {value}')
        self.magnitude = value
        return value

    def calculate_rhs(self):
        value = clause_calculator.calculate(self.rhs, self.state)
        logging.debug(f'calculated rhs value: {value}')
        self.rhs = value
        return value

    def calculate_lhs(self):
        value = clause_calculator.calculate(self.lhs, self.state)
        logging.debug(f'calculated lhs value: {value}')
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
        logging.info('got value_modification')
        return handler.process_value_modification(value_modification)
    elif conditional_value_modification:
        logging.info('got conditional_value_modification')
        return handler.process_conditional_value_modification(conditional_value_modification)
    else:
        raise ValueError(f'condition {condition} passed to evaluate_value_modification was not of a value modification form!')

def evaluate_state_modification(condition, state):
    handler = StateClauseHandler()
    handler.condition = condition
    handler.state = state
    handler.is_condition_valid = False
    state_modification = re.fullmatch(STATE_REGEXES['state_modification'], condition)
    conditional_state_modification = re.fullmatch(STATE_REGEXES['conditional_state_modification'], condition)

    if state_modification:
        logging.info('got state_modification')
        value = handler.process_state_modification(state_modification)
        return handler.target_state, value
    elif conditional_state_modification:
        logging.info('got conditional_state_modification')
        value = handler.process_conditional_state_modification(conditional_state_modification)
        return handler.target_state, value
    else:
        raise ValueError(f'condition {condition} passed to evaluate_state_modification was not of a state modification form!')

if __name__ == '__main__':
    set_up_logging.set_up_logging()

    for type, regex in STATE_REGEXES.items():
        logging.debug(f'{type} regex: {regex}')

    state = defaultdict(int, {'wealth': 10, 'money': 256, 'dogs': 1, 'cats': 3, 'fish': 12, 'name': 'Gabe'})
    print(evaluate_value_modification('%(10+wealth)*3>money-200->=dogs*(cats+fish)%', 100, state)) # 15
    print(evaluate_state_modification(' %(wealth+wealth/2*4)^2/2>money->cash:-=dogs*(cats+fish)%', state)) # -15
    print(evaluate_state_modification(' %(wealth+wealth/2*4)^2/2>-dogs->money:+=money-(dogs*252)%', state)) # 260
    print(evaluate_state_modification(' %name>"aaa"->whoami:=name%', state)) # 260
