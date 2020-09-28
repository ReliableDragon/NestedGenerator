import logging
import math
import re

import set_up_logging

SYMBOL_PRIORITY = {'(': 10, 'UM': 7, '^': 6, '*': 5, '/': 5, '+': 3, '-': 3, ')': 1}

def is_quoted_string(clause):
    return clause[0] == '"' and clause[-1] == '"'

def is_only_state(clause):
    return re.fullmatch('[a-zA-Z]\w+', clause)

def calculate(clause, state):
    if is_quoted_string(clause):
        logging.debug(f'Got lone string for {clause}.')
        return clause
    elif is_only_state(clause):
        logging.debug(f'Got lone state for {clause}.')
        return state[clause]

    logging.debug(f'Calculating value of expression {clause}, with state {state}.')
    op_stack = []
    val_stack = []
    stack = []

    # Strip space and add wrapping parens
    clause = clause.replace(' ', '')
    clause = '(' + clause + ')'

    curr_sym = ''

    for i, c in enumerate(clause):

        if c == '(':
            assert not curr_sym, f'Got an open paren at character {i} while current symbol was non-empty ({curr_sym}) while calculating {clause}!'
            op_stack.append(c)
            continue

        if c == '-' and not curr_sym:
            c = 'UM' #unary minus

        if c not in SYMBOL_PRIORITY.keys():
            curr_sym += c
            continue

        if curr_sym:
            try:
                val = float(curr_sym)
            except ValueError:
                val = state[curr_sym]
                assert isinstance(val, int), f'Got non-integer value {val} for state {curr_sym} when evaluating {clause}.'
            curr_sym = ''
            val_stack.append(val)

        while op_stack and (len(op_stack) == 1 or SYMBOL_PRIORITY[c] <= SYMBOL_PRIORITY[op_stack[-1]]) and op_stack[-1] != '(':
            operand = op_stack.pop()
            if operand == 'UM':
                to_negate = val_stack.pop()
                val_stack.append(-1 * to_negate)
                continue

            logging.debug(f'op_stack: {op_stack[-1]}')
            rhs = val_stack.pop()
            lhs = val_stack.pop()
            logging.debug(f'Calculating "{lhs} {operand} {rhs}".')

            if operand == '^':
                val_stack.append(lhs ** rhs)
            elif operand == '*':
                val_stack.append(lhs * rhs)
            elif operand == '/':
                val_stack.append(lhs / rhs)
            elif operand == '+':
                val_stack.append(lhs + rhs)
            elif operand == '-':
                val_stack.append(lhs - rhs)
            else:
                raise ValueError(f'Got unrecognized operand {operand} at character {i} while calculating {clause}!')

        if c == ')':
            assert op_stack[-1] == '(', f'Got close parenthesis at character {i} that didn\'t match with open parenthesis in current operand stack {op_stack} while calculating {clause}!'
            op_stack.pop()
        else:
            op_stack.append(c)

    assert len(op_stack) == 0, f'Operand stack expected to contain no elements, but was {op_stack} after calculating {clause}!'
    assert len(val_stack) == 1, f'Value stack expected to contain one element, but was {val_stack} after calculating {clause}!'
    logging.debug(f'Calculated value of {val_stack[-1]} for clause {clause}.')
    return math.floor(val_stack.pop())

if __name__ == '__main__':
    set_up_logging.set_up_logging()

    print(calculate('10-(10+thousand*wealth)', {'wealth': 10, 'thousand': 1000}))
    print(calculate('1+1*2+(2*(3/3+3))/thousand', {'wealth': 10, 'thousand': 1000}))
    print(calculate('(((((((2^5)))))))', {'wealth': 10, 'thousand': 1000}))
    print(calculate('"pretty pretty princesses"', {}))
    print(calculate('name', {'name': 'Gabe'}))
    print(calculate('-(1+-3*-4)', {}))
