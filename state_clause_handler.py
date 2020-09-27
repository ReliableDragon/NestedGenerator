import logging
import math
import re

VALID_COMPARISONS = ['==', '>=', '>', '<=', '<', '!=']


class StateClauseHandler():

    def __init__(self):
        self.condition = None
        self.lhs = None
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
    # def __init__(self, lhs, comparator, rhs, rhs_is_string_literal, rhs_is_state, effect, target_state, magnitude, magnitude_is_string_literal, magnitude_is_state, type):
    #     self.condition = None
    #     self.lhs = lhs
    #     self.comparator = comparator
    #     self.rhs = rhs
    #     self.rhs_is_string_literal = rhs_is_string_literal
    #     self.rhs_is_state = rhs_is_state
    #     self.target_state = target_state
    #     self.effect = effect
    #     self.magnitude = magnitude
    #     self.magnitude_is_string_literal = magnitude_is_string_literal
    #     self.magnitude_is_state = magnitude_is_state
    #     self.type = type
    #
    # def __init__(self, condition, state, base_value):
    #     self.init_fields()
    #     self.condition = condition
    #     self.state = state
    #     self.base_value = base_value
        # state_modification = re.match(' %([a-zA-Z]\w*):([+=\-/*])("?[\w ]+"?)%', condition)
        # conditional_state_modification = re.match(' %(\w+)([=<>!]+)("?[\w ]+"?)->([a-zA-Z]\w*):([+=\-/*])("?\w*"?)%', condition)
        # value_modification = re.match('%([-+=\/*])(\w+)%', condition)
        # conditional_value_modification = re.match('%(\w+)([=<>!]+)("?[\w]+"?)->([-+=\/*])(\w+)%', condition)
        #
        # if sum([state_modification, conditional_state_modification, value_modification, conditional_value_modification]) != 1:
        #     raise ValueError(f'Got condition {condition} that does not match exactly one proper format!')
        #
        # if state_modification:
        #     calculate_state_modification(state_modification)
        # elif conditional_state_modification:
        #     calculate_conditional_state_modification(conditional_state_modification)
        # elif value_modification:
        #     calculate_value_modification(value_modification)
        # elif conditional_value_modification:
        #     calculate_conditional_value_modification(conditional_value_modification)

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

    # def do_comparison(self, lhs, rhs, lhs_state=None, rhs_state=None):
    def do_comparison(self):
        assert self.type in ['conditional_state_modification', 'conditional_value_modification']
        assert self.comparator in VALID_COMPARISONS
        # if self.lhs_is_state:
        #     assert lhs_state, f'was not provided lhs_state when doing comparison for {self.condition}, which requires lhs_state'
        #     lhs = lhs_state
        # else:
        #     lhs = self.lhs
        # if self.rhs_is_state:
        #     assert rhs_state, f'was not provided rhs_state when doing comparison for {self.condition}, which requires rhs_state'
        #     rhs = rhs_state
        # else:
        #     rhs = self.rhs

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

    # def calculate_value_modification(self, base_value, magnitude_state=None):
    # def calculate_value_modification(self):
    #     assert self.type in ['value_modification', 'conditional_value_modification']
    #     assert self.is_condition_valid, f'Attempted to calculate value modification on {self.condition} while the condition was invalid! (Did you remember to calculate it before calling this method?)'
    #     assert self.base, f'was not provided base state when calculating value modification for {self.condition}, which requires base state'
    #     # if self.magnitude_is_state:
    #     #     assert magnitude_state, f'was not provided magnitude_state when calculating value modification for {self.condition}, which requires magnitude_state'
    #     #     magnitude = magnitude_state
    #     # else:
    #     #     magnitude = self.magnitude
    #     return self.calculate_modification(self.base)
    #
    #     # value = None
    #     # if self.effect == '*':
    #     #     value = self.base * self.magnitude
    #     # elif self.effect == '+':
    #     #     value = self.base + self.magnitude
    #     # elif self.effect == '*':
    #     #     value = self.base * self.magnitude
    #     # elif self.effect == '/':
    #     #     value = self.base / self.magnitude
    #     # elif self.effect == '=':
    #     #     value = self.magnitude
    #     #
    #     # if instanceof(value, int):
    #     #     value = math.max(value, 0)
    #     #
    #     # return value
    #
    # # def calculate_state_modification(self, base_value, target_state_value=None, magnitude_state=None):
    # def calculate_state_modification(self):
    #     assert self.type in ['state_modification', 'conditional_state_modification']
    #     # assert target_state_value, f'Attempted to calculate state modification on {self.condition} without providing the target state to calculate based on!'
    #     assert self.is_condition_valid, f'Attempted to calculate state modification on {self.condition} while the condition was invalid! (Did you remember to calculate it before calling this method?)'
    #     # if self.magnitude_is_state:
    #     #     assert magnitude_state, f'was not provided magnitude_state when calculating state modification for {self.condition}, which requires magnitude_state'
    #     #     magnitude = magnitude_state
    #     # else:
    #     #     magnitude = self.magnitude
    #
    #     return self.calculate_modification(self.target)

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

        if isinstance(value, int):
            value = max(value, 0)

        return value

    def set_up_magnitude(self):
        if self.magnitude[0] == '"':
            assert self.magnitude[-1] == '"', f'condition {self.condition} had mis-matched quotes.'
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
            assert self.rhs[-1] == '"', f'condition {condition} had mis-matched quotes.'
            self.rhs_is_string_literal = True
        else:
            try:
                self.rhs = int(self.rhs)
            except ValueError:
                self.rhs_is_state = True
                self.rhs = self.state[self.rhs]

    def set_up_lhs(self):
        logging.info(f'lhs={self.lhs}')
        try:
            self.lhs = int(self.lhs)
        except ValueError:
            self.lhs_is_state = True
            self.lhs = self.state[self.lhs]

    def init_fields(self):
        self.condition = None
        self.lhs = None
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

# @staticmethod
def evaluate_value_modification(condition, target, state):
    handler = StateClauseHandler()
    handler.init_fields()
    handler.condition = condition
    handler.target = target
    handler.state = state
    handler.is_condition_valid = False
    value_modification = re.match('%([-+=\/*])(\w+)%', condition)
    conditional_value_modification = re.match('%(\w+)([=<>!]+)("?[\w]+"?)->([-+=\/*])(\w+)%', condition)

    # if sum([value_modification, conditional_value_modification]) != 1:
    #     raise ValueError(f'Got condition {condition} that does not match exactly one proper format!')

    if value_modification:
        logging.info('got value_modification')
        return handler.process_value_modification(value_modification)
    elif conditional_value_modification:
        logging.info('got conditional_value_modification')
        return handler.process_conditional_value_modification(conditional_value_modification)
    else:
        raise ValueError(f'condition {condition} passed to evaluate_value_modification was not of a value modification form!')

# @staticmethod
def evaluate_state_modification(condition, state):
    handler = StateClauseHandler()
    handler.init_fields()
    handler.condition = condition
    handler.state = state
    handler.is_condition_valid = False
    state_modification = re.match(' %([a-zA-Z]\w*):([+=\-/*])("?[\w ]+"?)%', condition)
    conditional_state_modification = re.match(' %(\w+)([=<>!]+)("?[\w ]+"?)->([a-zA-Z]\w*):([+=\-/*])("?\w*"?)%', condition)

    # if sum([state_modification, conditional_state_modification]) != 1:
    #     raise ValueError(f'Got condition {condition} that does not match exactly one proper format!')

    if state_modification:
        logging.info('got state_modification')
        return handler.process_state_modification(state_modification)
    elif conditional_state_modification:
        logging.info('got conditional_state_modification')
        return handler.process_conditional_state_modification(conditional_state_modification)
    else:
        raise ValueError(f'condition {condition} passed to evaluate_state_modification was not of a state modification form!')
