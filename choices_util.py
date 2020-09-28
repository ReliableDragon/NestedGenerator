import logging
import re
import set_up_logging

def get_enclosing_braces(position, line, lbrace='{', rbrace='}'):
    logging.debug(f'Checking if position {position}, at the center of "{line[position-3:position+4]}" in line "{line}" is contained in braces.')
    lloc = None
    rloc = None
    i = position
    rbrace_count = 0
    while i >= 0:
        if line[i] == lbrace:
            rbrace_count -= 1
            if rbrace_count < 0:
                lloc = i
                break
        elif line[i] == rbrace:
            rbrace_count += 1
        i -= 1

    i = position
    lbrace_count = 0
    while i < len(line):
        if line[i] == rbrace:
            lbrace_count -= 1
            if lbrace_count < 0:
                rloc = i
                break
        elif line[i] == lbrace:
            lbrace_count += 1
        i += 1

    logging.debug(f'lloc: {lloc}, rloc: {rloc}')
    return lloc, rloc

def split_into_lines(s):
    return re.split('\r?\n', s)

def recursive_dict_print(dict, indent=0):
    val = ''
    indent_str = ' ' * indent
    for k, v in dict.items():
        val += indent_str + str(k) + ': {\n'
        val += recursive_dict_print(v, indent + 2)
        val += indent_str + '}\n'
    return val

def handle_brace_enclosure(target, to_replace, delete_all=False, lbrace='{', rbrace='}'):
    open, close = get_enclosing_braces(target, to_replace, lbrace, rbrace)
    if any([open, close]):
        assert open != None and close != None, f'Enclosing braces for target {target} in replacement string {to_replace} were not both found. Returned locations were {open}, {close}.'
        if delete_all:
            logging.debug(f'braces found, removing everything in {to_replace[open:close+1]}')
            to_replace = to_replace[:open] + to_replace[close+1:]
        else:
            # Remove the braces.
            to_replace = to_replace[:open] + to_replace[open+1:close] + to_replace[close+1:]
        return to_replace, open, close
    else:
        return to_replace, None, None

def backup_for_deletion(start, left_endpoint, right_endpoint):
    return start - min(max(0, start-right_endpoint), right_endpoint-left_endpoint+1)

def find_endpoint_for_interpolation(to_replace, start):
    end = len(to_replace)
    next = to_replace.find('$', start+1)
    if next != -1:
        end = next
    return end

def get_next_match(to_replace, pattern, start):
    end = find_endpoint_for_interpolation(to_replace, start)
    logging.debug(f'Getting next match for {pattern} in range {to_replace[start:end]}')
    match = pattern.search(to_replace, start, end)
    logging.debug(f'Found match {match}.')
    # while match:
    #     start = match.end()
    #     match = pattern.search(to_replace, start, end)
    #     logging.debug(f'Found match {match}.')
    return match

if __name__ == '__main__':
    set_up_logging.set_up_logging()

    print(get_enclosing_braces(3, '0{234}', '{', '}'))
    print(get_enclosing_braces(3, '0[234]'))
    print(get_enclosing_braces(5, '0{2}{567{}}', '{', '}'))
    print(get_enclosing_braces(5, '0123456789'))
    print(get_enclosing_braces(5, '0[23]5[78]'))
