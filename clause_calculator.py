import logging
import math
import re

import set_up_logging

PRIORITY = {
    '(': 99,
    '!': 8,
    'UM': 7,
    '^': 6,
    '*': 5,
    '/': 5,
    '+': 3,
    '-': 3,
    '==': 2,
    '!=': 2,
    '<':2,
    '>': 2,
    '>=': 2,
    '<=': 2,
    '&&': 1,
    '||': 0,
    ')': -99,
}
SYMBOL_PRIORITY = {'(': 10, 'UM': 7, '^': 6, '*': 5, '/': 5, '+': 3, '-': 3, ')': 1}
BOOLEAN_PRIORITY = {'(': 10, '==': 8, '!=': 8, '<':8, '>': 8, '>=': 8, '<=': 8, '&&': 7, '||': 6, ')': 1}
COMPARISON_SYMBOLS = '!=<>|&'
OPERAND_TOKENS = COMPARISON_SYMBOLS + '()^*/+-UM'

def calculate(clause, state):
    logging.debug(f'Calculating value of expression {clause}, with state {state}.')
    op_stack = []
    val_stack = []

    # Add wrapping parens
    clause = '(' + clause + ')'

    token = ''

    quoted = False

    i = -1
    while True:
        i += 1
        if i >= len(clause):
            break
        c = clause[i]
        # logging.debug(f'c: {c}, op_stack: {op_stack}, val_stack: {val_stack}, token: `{token}`, quoted: {quoted}')

        if c == '"':
            quoted = not quoted
        if quoted:
            token += c
            continue
        if c == ' ':
            continue

        if c == '(':
            # assert not token, f'Got an open paren at character {i} while current symbol was non-empty ({token}) while calculating {clause}!'
            op_stack.append(c)
            continue

        # TODO: Parentheses in the op_stack make this messy. e.g. age/(age_pct/100)<13 fails
        # when the close paren is read in, as the / is still on the op_stack. Rework it to be more readable.
        # assert not(not token and c in OPERAND_TOKENS and op_stack[-1] not in '()'), f'Got operand token {c} at character {i} with empty token while processing "{clause}"! Did you accidentally put two operations back-to-back?'

        if c == '-' and not token:
            c = 'UM' #unary minus
        if c == '!' and not token:
            c = 'NOT' #unary not

        if c not in OPERAND_TOKENS:
            token += c
            continue


        if token:
            if token[-1] == '"':
                val = token[1:-1]
            else:
                try:
                    val = float(token)
                except ValueError:
                    if token not in state.keys():
                        logging.info(f'Accessing token {token} that is not present in state {state}! This may be intentional use of the default property, or you may be using a token that is not yet defined. (Did you double check your spelling?)')
                    val = state[token]
                    try:
                        val = float(val)
                    except:
                        # String value was in state.
                        pass
                    # assert isinstance(val, int), f'Got non-integer value {val} for state {token} when evaluating {clause}.'
            token = ''
            val_stack.append(val)

        if c in COMPARISON_SYMBOLS and i != len(clause)-1 and clause[i+1] in COMPARISON_SYMBOLS:
            i += 1
            c += clause[i]
            # logging.debug(f'Got two-symbol comparator {c}.')

        while op_stack and (len(op_stack) == 1 or PRIORITY[c] <= PRIORITY[op_stack[-1]]) and op_stack[-1] != '(':
            operand = op_stack.pop()
            if operand == 'UM':
                to_negate = val_stack.pop()
                val_stack.append(-1 * to_negate)
                continue

            # logging.debug(f'op_stack: {op_stack[-1]}')
            rhs = val_stack.pop()
            lhs = val_stack.pop()
            logging.debug(f'Calculating "{lhs} {operand} {rhs}".')

            if isinstance(rhs, str):
                lhs = try_int_conversion(lhs)
                lhs = str(lhs)
            elif isinstance(lhs, str):
                rhs = try_int_conversion(rhs)
                rhs = str(rhs)

            if operand == '^':
                value = lhs ** rhs
            elif operand == '*':
                value = lhs * rhs
            elif operand == '/':
                value = lhs / rhs
            elif operand == '+':
                value = lhs + rhs
            elif operand == '-':
                value = lhs - rhs
            elif operand == '||':
                value = lhs or rhs
            elif operand == '&&':
                value = lhs and rhs
            elif operand == '==':
                value = lhs == rhs
            elif operand == '!=':
                value = lhs != rhs
            elif operand == '>':
                value = lhs > rhs
            elif operand == '<':
                value = lhs < rhs
            elif operand == '>=':
                value = lhs >= rhs
            elif operand == '<=':
                value = lhs <= rhs
            elif operand == 'NOT':
                value = not value
            else:
                raise ValueError(f'Got unrecognized operand {operand} at character {i} while calculating {clause}!')

            # logging.debug(f'Calculated "{value}".')
            val_stack.append(value)

        if c == ')':
            assert op_stack[-1] == '(', f'Got close parenthesis at character {i} that didn\'t match with open parenthesis in current operand stack {op_stack} while calculating {clause}!'
            op_stack.pop()
        else:
            op_stack.append(c)

    assert len(op_stack) == 0, f'Operand stack expected to contain no elements, but was {op_stack} after calculating {clause}!'
    assert len(val_stack) == 1, f'Value stack expected to contain one element, but was {val_stack} after calculating {clause}!'
    logging.debug(f'Calculated value of {val_stack[-1]} for clause {clause}.')

    result = val_stack.pop()
    result = try_int_conversion(result)
    # if isinstance(result, float):
    #     try:
    #         result = math.floor(result)
    #     except TypeError:
    #         # It's a string
    #         pass
    return result

def try_int_conversion(maybe_num):
    try:
        return math.floor(maybe_num)
    except TypeError:
        # It's a string
        return maybe_num


if __name__ == '__main__':
    set_up_logging.set_up_logging()

    print(calculate('10-(10+thousand*wealth)', {'wealth': 10, 'thousand': 1000})) # -10000
    print(calculate('1+1*2+(2*(3/3+3))/thousand', {'wealth': 10, 'thousand': 1000})) # 3
    print(calculate('(((((((2^5)))))))', {'wealth': 10, 'thousand': 1000})) #32
    print(calculate('"pretty pretty princesses"', {})) # see title
    print(calculate('name', {'name': 'Gabe'})) # Gabe
    print(calculate('-(1+-3*-4)', {})) # -13
    print(calculate('"test" + "test"', {})) # testtest
    print(calculate('"data: " + data', {'data': 12345})) # data: 12345
    print(calculate('"12345" == "123" + fourfive', {'fourfive': 45}))
    print(calculate('"abhorent" > "bad" && (12 + (dogs * cats) == 12 * 6 && "meemo" == "me" + "moo")', {'dogs': 2, 'cats': 3}))
    print(calculate('!"True" == "False"', {})) # We don't have booleans, so unary NOT is pretty useless. But technically included.
