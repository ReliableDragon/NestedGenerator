import re
import random
import uuid
import math

class WeightedChoice():
    def __init__(self, weight, choice, tag=1):
        self.weight = int(weight)
        self.choice = choice
        self.tag = tag

    def __str__(self):
        return f'({self.weight})[{self.tag}] "{self.choice}"'

    def __repr__(self):
        return self.__str__()


class NestedChoices():

    def __init__(self, namespace_id, choices_tree={}):
        self.namespace_id = namespace_id
        self.choices = choices_tree
        self.subtables = {}

    def __str__(self):
        val = '{\n'
        indent = 2
        val += recursive_dict_print(self.choices, indent)
        val += '}'

        return val

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def load_from_file(filename):
        with open(filename, 'r', encoding='utf-8') as choices_file:
            choices_string = choices_file.read()
            namespace_id = choices_string.split('\n', 1)[0]
            #Strip the id off.
            choices_string = choices_string.split('\n', 2)[2]
            validate_choices(namespace_id, choices_string)
            choices_tree = NestedChoices.choices_string_to_tree(choices_string)

        return NestedChoices(namespace_id, choices_tree)

    @staticmethod
    def choices_string_to_tree(choices_string):
        choices_tree = {}

        top_level_choices_list = choices_string.split('\n\n')
        top_level_choices_list = [choice.strip() for choice in top_level_choices_list]
        for top_level_choice_data in top_level_choices_list:
            indent = 0
            parent_choicedict_stack = [choices_tree]

            nested_choices = split_into_lines(top_level_choice_data)
            top_level_choice = nested_choices.pop(0)

            try:
                parent = WeightedChoice(*top_level_choice.split(' ', 1))
            except TypeError:
                # Empty choice.
                parent = WeightedChoice(top_level_choice, '')

            choices_tree[parent] = {}
            current_dict = choices_tree[parent]
            # Holds the value to go back to if the next node turns out to be a leaf.
            prev_dict = choices_tree
            tag_stack = [1]

            for choice in nested_choices:
                # Check how many spaces there are to find the indent level.
                new_indent = len(choice) - len(choice.lstrip(' '))


                if new_indent == indent:
                    # print("same")
                    current_dict = prev_dict
                elif new_indent > indent:
                    # print("indent")
                    parent_choicedict_stack.append(current_dict)
                    tag_stack.append(1)
                    # If there's a same indent next, this is the level we want to be on.
                    prev_dict = current_dict
                elif new_indent < indent:
                    # print("dedent")
                    distance_up_stack = (indent - new_indent) // 2
                    for _ in range(distance_up_stack):
                        parent_choicedict_stack.pop()
                        tag_stack.pop()
                    current_dict = parent_choicedict_stack[-1]
                    # If there's a same indent next, this is the level we want to be on.
                    prev_dict = current_dict
                indent = new_indent
                # print(f'TSpost: {tag_stack}')

                if is_tag_marker(choice):
                    tag_stack[-1] += 1
                    continue

                choice = choice[new_indent:]
                try:
                    weighted_choice = WeightedChoice(*choice.split(' ', 1), tag=tag_stack[-1])
                except TypeError:
                    # Empty choice.
                    weighted_choice = WeightedChoice(choice, '', tag_stack[-1])

                current_dict[weighted_choice] = {}
                current_dict = current_dict[weighted_choice]


        return choices_tree

    @staticmethod
    def load_from_string_list(namespace_id, choices, probs=[]):
        if probs:
            assert len(probs) == len(choices), 'Got a list of probabilities that was not the same length as the list of choices!'
            choices = [str(prob) + ' ' + choice for prob, choice in zip(probs, choices)]
        else:
            choices = ['1 ' + s for s in choices]
        choices_string = '\n\n'.join(choices)
        validate_choices(namespace_id, choices_string)
        choices_tree = NestedChoices.choices_string_to_tree(choices_string)

        return NestedChoices(namespace_id, choices_tree)

    def register_subtable(self, nc):
        self.subtables[nc.namespace_id] = nc

    # Given a nested choices string from get_choices, randomly generates a choice
    # from it. Parameters can be passed to affect how it runs.
    #
    # 'num' says how many choices to generate
    #
    # 'uniqueness_level' says at what level the returned choices should be
    # unique. -1 means the lowest level, simply don't repeat the exact same
    # choice, while positive values starting from 1 indicate which level
    # of indentation will be removed if a previous choice chose it. A level of
    # 0 indicates that repetition is okay.
    #
    # 'uniqueness_mode' can be 'each' or 'all'. 'all' means that uniqueness should
    # only consider the choice as a whole, while 'each' means that each table
    # has the uniqueness constraint applied to it. For example, a pattern of
    # '$ a $' would be allowed to generate '1 a 2' and '1 a 3' under 'all', but
    # under 'each' that would not be allowed, since the first value repeated itself.
    # Not yet implemented.
    def gen_choice(self, params={'num': 1, 'uniqueness_level': -1, 'uniqueness_mode':'each'}):
        generated_choices = []
        used_choices = []

        for i in range(params['num']):
            generated = False
            generated_choice = '$'
            dict_and_choice_backtrace = []
            level = 1
            choices_dict = self.choices

            generated_choice = generation_step(generated_choice, dict_and_choice_backtrace, used_choices, level, choices_dict, params)
            generated_choice = self.make_replacements(generated_choice)
            generated_choices.append(generated_choice)

        if params['num'] == 1:
            return generated_choice
        else:
            return generated_choices

    def make_replacements(self, generated_choice):
        generated_choice = replace_ranges(generated_choice)
        generated_choice = self.make_subtable_calls(generated_choice)

        return generated_choice

    def make_subtable_calls(self, generated_choice):
        subtable_replace = re.compile('@([\w_]+)')
        match = subtable_replace.search(generated_choice)
        while match:
            full_match = match.group(0)
            subtable_id = match.group(1)

            subtable = self.subtables[subtable_id]

            generated_choice = generated_choice.replace(full_match, subtable.gen_choice())
            match = subtable_replace.search(generated_choice)
        return generated_choice

def generation_step(generated_choice, dict_and_choice_backtrace, used_choices, level, choices_dict, params):
    if '$' not in generated_choice:
        return generated_choice

    tags = list(range(1, generated_choice.count('$') + 1))
    filtered_choice_lists = [list(filter(lambda c: c not in used_choices and c.tag == tag, choices_dict)) for tag in tags]
    weighted_choice_lists = [pick_choice(filtered_choice) for filtered_choice in filtered_choice_lists]
    recursed_choice_list = []

    for weighted_choice in weighted_choice_lists:
        if level == params['uniqueness_level']:
            used_choices.append(weighted_choice)
            remove_childless_parents(dict_and_choice_backtrace, used_choices)
        # If there's nothing in the corresponding list, we're at a leaf node
        # and are done generating this choice.
        if not choices_dict[weighted_choice]:
            if params['uniqueness_level'] == -1:
                used_choices.append(weighted_choice)
                remove_childless_parents(dict_and_choice_backtrace, used_choices)

        dict_and_choice_backtrace.append((choices_dict, weighted_choice))
        recursed_choice = generation_step(weighted_choice.choice, dict_and_choice_backtrace, used_choices, level+1, choices_dict[weighted_choice], params)
        recursed_choice_list.append(recursed_choice)
        dict_and_choice_backtrace.pop()

    for choice in recursed_choice_list:
        generated_choice = generated_choice.replace('$', choice, 1)

    return generated_choice

def replace_ranges(generated_choice):
    num_replace = re.compile('\[(\d+)-(\d+)(G|N)?\]')
    match = num_replace.search(generated_choice)
    while match:
        full_match = match.group(0)
        start = int(match.group(1))
        end = int(match.group(2))
        type = match.group(3)

        val = None
        if type == 'N':
            # start = mean, end = stddev
            val = math.floor(random.gauss(start, end))
        elif type == 'G':
            #start = alpha, end = beta
            val = math.floor(random.gammavariate(start, end))
        else:
            val = random.randint(start, end)

        generated_choice = generated_choice.replace(full_match, str(val))
        match = num_replace.search(generated_choice)
    return generated_choice

def is_tag_marker(choice):
    return re.match('(  )+\$', choice)

def pick_choice(filtered_choices):
    total_weight = sum([wc.weight for wc in filtered_choices])
    assert total_weight > 0, f'Total weight was <= 0, most likely you wrote a generation that removed all valid choices from a config. Choices given were: {filtered_choices}'
    rand = random.randint(1, total_weight)

    for wc in filtered_choices:
        rand -= wc.weight
        if rand <= 0:
            return wc

# This one's a bit tricky. We take in a backtrace object which contains a trail of WCs
# that we may have to remove, and the dictionaries that they occur in. Starting from the
# bottom up, we look up the values under each WC in its parent dictionary, which lets us
# check if there are any left uncovered. If there are, then we break. Otherwise, we will
# use the dictionary to remove the WC, and go up another level to check again.
def remove_childless_parents(dict_and_choice_backtrace, used_choices):
    for dict, wc in dict_and_choice_backtrace[::-1]:
        if len(list(filter(lambda d: d not in used_choices, dict[wc].keys()))) != 0:
            break
        used_choices.append(wc)

def recursive_dict_print(dict, indent=0):
    val = ''
    indent_str = ' ' * indent
    for k, v in dict.items():
        val += indent_str + str(k) + ': {\n'
        val += recursive_dict_print(v, indent + 2)
        val += indent_str + '}\n'
    return val

def gen_choice_bak(self, params={'num': 1, 'uniqueness_level': -1}):
    generated_choices = []
    used_choices = []

    for i in range(params['num']):
        generated = False
        generated_choice = '$'
        dict_and_choice_backtrace = []
        level = 0
        choices_dict = self.choices

        # generated_choice = generation_step(generated_choice, dict_and_choice_backtrace, )
        while not generated:
            level += 1
            filtered_choices = list(filter(lambda c: c not in used_choices, choices_dict))

            weighted_choice = pick_choice(filtered_choices)

            if level == params['uniqueness_level']:
                used_choices.append(weighted_choice)
                remove_childless_parents(dict_and_choice_backtrace, used_choices)

            generated_choice = self.make_replacements(generated_choice, weighted_choice)
            # If there's nothing in the corresponding list, we're at a leaf node
            # and are done generating this choice.
            if not choices_dict[weighted_choice]:
                if params['uniqueness_level'] == -1:
                    used_choices.append(weighted_choice)
                    remove_childless_parents(dict_and_choice_backtrace, used_choices)
                generated = True
            else:
                dict_and_choice_backtrace.append((choices_dict, weighted_choice))
                choices_dict = choices_dict[weighted_choice]

        generated_choices.append(generated_choice)

    if params['num'] == 1:
        return generated_choice
    else:
        return generated_choices

def load_from_file_bak(filename):
    with open(filename, 'r', encoding='utf-8') as choices_file:
        choices_string = choices_file.read().split('\n\n')
        choices_string = [choice.strip() for choice in choices_string]
        # weights_and_choices = [choice.split(' ', 1) for choice in choices_string]
        # weighted_choices = list(map(lambda wandp: (int(wandp[0]), wandp[1]), weights_and_choices))
    return weighted_choices

def validate_choices(namespace_id, choices_string):
    assert len(choices_string) != 0, 'Got empty choices data!'
    lines = choices_string.split('\n')
    must_indent = False
    prev_indent = 0
    blank = False

    for line in lines:
        if line == '':
            if blank:
                raise Error(f'Found two blank lines in a row in {namespace_id}.')
            blank == True
            continue

        blank == False
        indent = len(line) - len(line.lstrip(' '))
        if must_indent:
            assert indent == prev_indent + 2, f'Line {line} in {namespace_id} did not indent, despite a symbol requiring indentation on the previous line.'
            must_indent = False
        else:
            assert indent % 2 == 0 and indent < prev_indent + 2, f'Line {line} in {namespace_id} in  has an improper number of spaces.'

        assert re.match(f' *(\d+|\$)', line), f'Line {line} in {namespace_id} failed to match the expected format.'

        if '$' in line and line != (' ' * indent) + '$':
            must_indent = True

        prev_indent = indent

def split_into_lines(s):
    return re.split('\r?\n', s)

if __name__ == "__main__":
    choices = NestedChoices.load_from_file('test_places.txt')
    subtable = NestedChoices.load_from_string_list('countries_table', ['Germany', 'France', 'UK'], [5, 3, 1])
    choices.register_subtable(subtable)
    print(choices.gen_choice(params={'num': 4, 'uniqueness_level': -1}))
