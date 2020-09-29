import logging
import math
import re

import clause_calculator
import set_up_logging
import choices_util

from state_regexes import STATE_REGEXES

from collections import defaultdict

class StateClauseHandler():

    def __init__(self):
        self.condition = None
        self.choice_value = None
        self.condition = None
        self.target_state = None
        self.target =  None
        self.effect = None
        self.magnitude = None
        self.type = None

    def process_conditional_value_modification(self, match):
        self.type = 'conditional_value_modification'
        self.condition = match.group(1)
        self.effect = match.group(2)
        self.magnitude = match.group(3)

        self.calculate_condition()
        self.calculate_magnitude()

        if self.condition:
            return self.calculate_modification()
        else:
            return self.target

    def process_value_modification(self, match):
        self.type = 'value_modification'
        self.effect = match.group(1)
        self.magnitude = match.group(2)

        self.calculate_magnitude()

        return self.calculate_modification()

    def process_conditional_state_modification(self, match):
        self.type = 'conditional_state_modification'
        self.condition = match.group(1)
        self.target_state = match.group(2)
        self.target = self.state[self.target_state]
        self.effect = match.group(3)
        self.magnitude = match.group(4)

        # Unary effect
        if match.group(5):
            self.effect = match.group(5)

        self.calculate_condition()
        if self.magnitude:
            self.calculate_magnitude()

        if self.condition:
            return self.calculate_modification()
        else:
            return self.target

    def process_state_modification(self, match):
        self.type = 'state_modification'
        self.target_state = match.group(1)
        self.target = self.state[self.target_state]
        self.effect = match.group(2)
        self.magnitude = match.group(3)

        # Unary effect
        if match.group(4):
            self.effect = match.group(4)

        if self.magnitude:
            self.calculate_magnitude()

        return self.calculate_modification()

    def process_conditional_state_interpolation(self, match):
        self.type = 'conditional_state_interpolation'
        self.condition = match.group(1)
        self.magnitude = match.group(2)

        self.calculate_condition()
        self.calculate_magnitude()

        if self.magnitude == None or not self.condition:
            # logging.debug('Comparison was false!')
            return None
        else:
            return self.magnitude

    def process_state_interpolation(self, match):
        self.type = 'state_interpolation'
        self.target_state = match.group(1)

        if self.target_state not in self.state.keys():
            return None
        else:
            return self.state[self.target_state]

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
        elif self.effect == '@':
            value = self.choice_value
        else:
            raise ValueError(f'Got unrecognized effect {self.effect} while handling {self.condition}!')

        # logging.debug(f'Calculated modification of {value}')

        return value

    def calculate_magnitude(self):
        value = clause_calculator.calculate(self.magnitude, self.state)
        self.magnitude = value
        # logging.debug(f'Calculated magnitude: {self.magnitude}')
        return value

    def calculate_condition(self):
        value = clause_calculator.calculate(self.condition, self.state)
        self.condition = value
        return value


def evaluate_value_modification(condition, target, state):
    assert '@' not in condition, f'"@" provided in value modification {condition}, which is not allowed. "@" is only allowed in state modification.'
    handler = StateClauseHandler()
    handler.condition = condition
    handler.target = target
    handler.state = state
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

def evaluate_state_modification(condition, choice_value, state):
    handler = StateClauseHandler()
    handler.condition = condition
    handler.state = state
    handler.choice_value = choice_value
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

def evaluate_state_interpolation(condition, state):
    # logging.debug(f'Calculating interpolation value for "{condition}".')
    handler = StateClauseHandler()
    handler.condition = condition
    handler.state = state
    state_interpolation = re.fullmatch(STATE_REGEXES['state_interpolation'], condition)
    conditional_state_interpolation = re.fullmatch(STATE_REGEXES['conditional_state_interpolation'], condition)
    plain_state_interpolation = re.fullmatch(STATE_REGEXES['plain_state_interpolation'], condition)

    if plain_state_interpolation:
        # If we get a stand-alone state, we only display it if it's present in the dictionary.
        # We don't display default values for these.
        state_name = plain_state_interpolation.group(2)
        if state_name not in state.keys():
            return None

    if state_interpolation:
        # logging.info('got state_interpolation')
        value = handler.process_state_interpolation(state_interpolation)
        return value
    elif conditional_state_interpolation:
        # logging.info('got conditional_state_interpolation')
        value = handler.process_conditional_state_interpolation(conditional_state_interpolation)
        return value
    else:
        raise ValueError(f'condition "{condition}" passed to evaluate_state_interpolation was not of a state interpolation form!')


def process_state_tag(choice_to_expand, tag):
    # logging.debug(f'Processing state tag for tag {tag} on {choice_to_expand}')
    start = choice_to_expand.find(tag.symbol)
    tag_end = start + len(tag.symbol)
    tag_truncated_choice = choice_to_expand[tag_end:]
    # logging.debug(f'tag_truncated_choice {tag_truncated_choice}')
    pattern = re.compile(STATE_REGEXES['tag_state'])
    match = pattern.match(choice_to_expand, tag_end)
    if match:
        # logging.debug(f'Got match {match}')
        state_to_update = match.group(1)
        choice_to_expand = choice_to_expand[:match.start()] + choice_to_expand[match.end():]
        return choice_to_expand, state_to_update
    else:
        # logging.debug(f'No match')
        return choice_to_expand, None

def clause_list_from_raw_clause(raw_clause):
    return ['%' + clause + '%' for clause in raw_clause.split('|')]

if __name__ == '__main__':
    args = set_up_logging.set_up_logging(['--dump_regexes'])

    if args.dump_regexes:
        for type, regex in STATE_REGEXES.items():
            print(f'{type} regex: "{regex}"')
        exit()

    state = defaultdict(int, {'wealth': 10, 'money': 256, 'dogs': 1, 'cats': 3, 'fish': 12, 'name': 'Gabe'})
    print(evaluate_value_modification('%(10+wealth)*3>money-200->=dogs*(cats+fish)%', 100, state)) # 15
    print(evaluate_state_modification(' %(wealth+wealth/2*4)^2/2>money->cash:-=dogs*(cats+fish)%', 'choice', state)) # -15
    print(evaluate_state_modification(' %(wealth+wealth/2*4)^2/2>-dogs->money:+=money-(dogs*252)%', 'choice', state)) # 260
    print(evaluate_state_modification(' %name>"aaa"->whoami:=name%', 'choice', state)) # 260
