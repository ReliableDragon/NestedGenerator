import logging
import re

import set_up_logging

def parse_from_string(choice_string):
    pass


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
