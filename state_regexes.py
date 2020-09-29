SPECIAL_CHARS = '[ \(\)]'
STATE_RE = '(?:[a-zA-Z]\w+)'
QUOTED_STRING = '(?:"[^%]+?")'
FULL_OPERATORS = '(?:\*|\+|\-|/|\^|&&|\|\|)'
FULL_VALUES = f'(?:{QUOTED_STRING}|\-?{STATE_RE}|\-?\d+)'
FULL_OPERATIONS = f'(?:{SPECIAL_CHARS}*{FULL_VALUES}{SPECIAL_CHARS}*{FULL_OPERATORS})*{SPECIAL_CHARS}*{FULL_VALUES}{SPECIAL_CHARS}*'
FULL_COMPARATORS = '(?:==|!=|>=|<=|>|<)'
FULL_COMPARISON = f'((?:{SPECIAL_CHARS}*{FULL_OPERATIONS}{SPECIAL_CHARS}*{FULL_COMPARATORS})*{SPECIAL_CHARS}*{FULL_OPERATIONS}{SPECIAL_CHARS}*)'
MATH_CALCULATION = '[\^\-\+/\*\(\)0-9\w]+'
STRING_CALCULATION = '(?:(?:"[^%]+?")|\+|(?:[a-zA-Z]\w+))+'
CALCULATION_CLAUSE_RE = f'({MATH_CALCULATION}|{STRING_CALCULATION})'
COMPARATOR_RE = '([=<>!]{1,2})'
EFFECT_RE = '([\^\-\+/\*]=|=)'
CURRENT_VALUE_RE = '@'
CONDITION_RE = f'{CALCULATION_CLAUSE_RE}{COMPARATOR_RE}{CALCULATION_CLAUSE_RE}'
STATE_MOD_EFFECT_RE = f'({STATE_RE}):(?:{EFFECT_RE}{FULL_COMPARISON}|({CURRENT_VALUE_RE}))'

VALID_COMPARISONS = ['==', '>=', '>', '<=', '<', '!=']
STATE_REGEXES = {
    'value_modification': f'%{EFFECT_RE}{FULL_COMPARISON}%',
    'conditional_value_modification': f'%{FULL_COMPARISON}->{EFFECT_RE}{FULL_COMPARISON}%',
    'omni_value_modification': f'%(?:{FULL_COMPARISON}->)?{EFFECT_RE}{FULL_COMPARISON}%',

    'state_modification': f' %{STATE_MOD_EFFECT_RE}%',
    'conditional_state_modification': f' %{FULL_COMPARISON}->{STATE_MOD_EFFECT_RE}%',
    'omni_state_modification': f' %(?:{FULL_COMPARISON}->)?{STATE_MOD_EFFECT_RE}%',

    'state_interpolation': f'%{FULL_COMPARISON}%',
    'conditional_state_interpolation': f'%{FULL_COMPARISON}->{FULL_COMPARISON}%',
    'omni_state_interpolation': f'%(?:({FULL_COMPARISON})(?:->))?{FULL_COMPARISON}%',

    'plain_state_interpolation': f'%(?:{FULL_COMPARISON}->)?({STATE_RE})%',
    'tag_state': f'%({STATE_RE}):({CURRENT_VALUE_RE})%'
}
