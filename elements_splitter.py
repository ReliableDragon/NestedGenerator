import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def split_into_tokens(elements):
    logger.debug(f'Parsing elements "{elements}".')
    result = []
    quoted = False
    parens = 0
    token = ''
    i = -1
    # for i, c in enumerate(elements):
    while i < len(elements)-1:
        i += 1
        c = elements[i]
        logger.debug(f'Processing character "{c}", quoted = {quoted}, parens = {parens}, token = "{token}", result = {result}.')

        if c == ' ':
            if token:
                logger.debug(f'Adding token "{token}" to results.')
                result.append(token)
            token = ''
            continue

        token += c

        if c == '"':
            while len(token) == 1 or c != '"':
                i += 1
                c = elements[i]
                token += c

        if c == '*':
            while elements[i+1].isnumeric():
                i += 1
                c = elements[i]
                token += c
            result.append(token)
            token = ''

        if c == '/':
            result.append(token)
            token = ''

        if c == '(' or c == '[':
            open_paren = c
            if open_paren == '(':
                close_paren = ')'
            else:
                close_paren = ']'
            parens += 1
            while parens > 0:
                i += 1
                c = elements[i]
                if c == open_paren:
                    parens += 1
                if c == close_paren:
                    parens -= 1
                token += c
            logger.debug(f'Processing parenthetized clause "{token}".')
            if open_paren == '(':
                token = split_into_tokens(token[1:-1])
            else:
                result.append('[')
                result.append(split_into_tokens(token[1:-1]))
                token = token[-1]

    if token:
        result.append(token)
    logger.debug(f'Returning results "{result}".')

    return result
