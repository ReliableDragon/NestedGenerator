import logging
import math
import re

VALID_COMPARISONS = ['==', '>=', '>', '<=', '<', '!=']
STATE_REGEXES = {
    'value_modification': '%([-+=\/*])(\w+)%',
    'conditional_value_modification': '%("?[\w ]+"?)([=<>!]+)("?[\w]+"?)->([-+=\/*])(\w+)%',
    'state_modification': ' %([a-zA-Z]\w*):([+=\-/*])("?[\w ]+"?)%',
    'conditional_state_modification': ' %("?[\w ]+"?)([=<>!]+)("?[\w ]+"?)->([a-zA-Z]\w*):([+=\-/*])("?\w*"?)%',
}


class StateClauseHandler():

    def __init__(self):
        self.condition = None
        self.lhs = None
        self.lhs_is_string_literal = None
        self.lhs_is_state = None
        self.comparator = None
        self.rhs = None
        self.rhs_is_string_literal = None
        self.rhs_is_state = None
        self.target_state = None
        self.target =  None
        self.effect = None
        self.magnitude = None
        self.magnitude_is_string_literal = None
        self.magnitude_is_state = None
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

        self.set_up_lhs()
        self.set_up_rhs()
        self.set_up_magnitude()

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

        self.set_up_magnitude()

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

        self.set_up_lhs()
        self.set_up_rhs()
        self.set_up_magnitude()

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

        self.set_up_magnitude()

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
        if self.effect == '*':
            value = self.target * self.magnitude
        elif self.effect == '+':
            value = self.target + self.magnitude
        elif self.effect == '*':
            value = self.target * self.magnitude
        elif self.effect == '/':
            value = self.target / self.magnitude
        elif self.effect == '=':
            value = self.magnitude

        return value

    def set_up_magnitude(self):
        if self.magnitude[0] == '"':
            assert self.magnitude[-1] == '"', f'condition {self.condition} had mis-matched quotes on the magnitude.'
            self.magnitude_is_string_literal = True
        else:
            try:
                self.magnitude = int(self.magnitude)
            except ValueError:
                self.magnitude_is_state = True
                self.magnitude = self.state[self.magnitude]

    def set_up_rhs(self):
        logging.info(f'rhs={self.rhs}')
        if self.rhs[0] == '"':
            assert self.rhs[-1] == '"', f'condition {condition} had mis-matched quotes on the rhs.'
            self.rhs_is_string_literal = True
        else:
            try:
                self.rhs = int(self.rhs)
            except ValueError:
                self.rhs_is_state = True
                self.rhs = self.state[self.rhs]

    def set_up_lhs(self):
        logging.info(f'lhs={self.lhs}')
        if self.lhs[0] == '"':
            assert self.lhs[-1] == '"', f'condition {condition} had mis-matched quotes on the lhs.'
            self.lhs_is_string_literal = True
        else:
            try:
                self.lhs = int(self.lhs)
            except ValueError:
                self.lhs_is_state = True
                self.lhs = self.state[self.lhs]

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
