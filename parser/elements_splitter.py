import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Takes in a string in ABNF(ish) format, and parses it into individual tokens,
# grouping them into sub-lists to indicate control character grouping.
def split_into_tokens(elements):
    logger.debug(f'Parsing elements "{elements}".')
    result = []
    partial_result = []
    quoted = False
    parens = 0
    token = ''
    i = -1

    while i < len(elements)-1:
        i += 1
        c = elements[i]
        logger.debug(f'Processing character "{c}", quoted = {quoted}, parens = {parens}, token = "{token}", result = {result}, partial_result = {partial_result}.')

        # On a space, add the current token to the result. If there is anything in
        # partial_result, then we have a modifier, and need to add a sub-list starting
        # with that modifier, to indicate to the parser that these things are grouped.
        if c == ' ':
            if partial_result:
                partial_result.append(token)
                logger.debug(f'Adding multi result "{partial_result}" to results.')
                result.append(partial_result)
                partial_result = []
            elif token:
                logger.debug(f'Adding token "{token}" to results.')
                result.append(token)
            token = ''
            continue

        token += c

        # Quoted strings can contain anything, so simply process onward until we reach
        # the matching quote.
        if c == '"':
            while len(token) == 1 or c != '"':
                i += 1
                c = elements[i]
                token += c
        # An asterisk or digit means repetition. We keep reading, to grab the whole
        # repetition clause, and then put it in partial_results to be prepended
        # to the next token in a sub-list, so the parser knows they are linked together.
        elif c == '*' or c.isnumeric():
            while elements[i+1].isnumeric() or elements[i+1] == '*':
                i += 1
                c = elements[i]
                token += c
            logger.debug(f'Adding token "{token}" to partial_results.')
            partial_result.append(token)
            token = ''
        # A slash is the alternative marker, and will always appear alone. (Unless
        # in a quoted string.)
        elif c == '/':
            result.append(token)
            token = ''
        # Parentheses and brackets both group tokens together, with the added effect
        # that brackets mark the tokens as optional. (Equivalent to *1.) We put all
        # of the grouped tokens into a sublist, so that the parser knows they go
        # together (and can easily recurse on them). Since whatever appears within
        # parentheses/braces is effectively just another token list, we can simply
        # recurse over it.
        elif c == '(' or c == '[':
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
                sub_tokens = split_into_tokens(token[1:-1])
            else:
                sub_tokens = ['[', *split_into_tokens(token[1:-1]), ']']

            # Don't forget to prepend the partial result if there is one! They can
            # apply to grouped tokens too! This also adds another layer of list nesting,
            # to indicate that the partial result token applies to the whole grouped
            # token list.
            if partial_result:
                sub_tokens = partial_result + [sub_tokens]
                partial_result = []

            result.append(sub_tokens)
            token = ''

    # Post loop read, to process anything still left in the token/partial_result
    # buffers.
    if partial_result:
        partial_result.append(token)
        logger.debug(f'Adding multi result "{partial_result}" to results.')
        result.append(partial_result)
    elif token:
        logger.debug(f'Adding token "{token}" to results.')
        result.append(token)
    logger.debug(f'Returning results "{result}".')

    return result
