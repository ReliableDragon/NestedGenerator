import re
import random
import uuid
import math
import logging
import argparse

import state_clause_handler
import choices_util
import choices_validator
import choice_generator as choice_generator_mod
from state_regexes import STATE_REGEXES

class WeightedChoice():
    def __init__(self, weight, choice, tag_num=1, clause=None):
        self.weight = int(weight)
        self.choice = choice
        self.tag_num = tag_num
        self.clause = clause
        self.uuid = uuid.uuid4()

    def __str__(self):
        str_rep = f'({self.weight})[{self.tag_num}]'
        if self.clause:
            str_rep += f'{{{self.clause}}}'
        str_rep += f'{self.choice}'
        return str_rep

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
        val += choices_util.recursive_dict_print(self.choices, indent)
        val += '}'

        return val

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def load_from_file(filename):
        with open(filename, 'r', encoding='utf-8') as choices_file:
            choices_string = choices_file.read()

        # Remove comments
        choices_string = re.sub('(\n *)? *#.*$', '', choices_string, flags=re.MULTILINE)
        # print(choices_string)

        # Strip the namespace id off
        namespace_id = choices_string.split('\n', 1)[0]

        choices_string = choices_string.split('\n', 1)[1]

        import_files = []
        while ':' in choices_string[:choices_string.index('\n')]:
            logging.debug(f'Importing from choices_string (trunc): {choices_string[:50]}')
            required_module = choices_string.split('\n', 1)[0]
            module_filename = required_module.split(':')[1]
            #Strip the import off.
            choices_string = choices_string.split('\n', 1)[1]
            import_files.append(module_filename)

        # Strip off the leading newline.
        choices_string = choices_string.split('\n', 1)[1]

        choices_validator.validate_choices(namespace_id, choices_string)
        choices_tree = NestedChoices.choices_string_to_tree(choices_string)

        resulting_nested_choices = NestedChoices(namespace_id, choices_tree)

        for filename in import_files:
            imported_choice = NestedChoices.load_from_file(filename)
            resulting_nested_choices.register_subtable(imported_choice)

        return resulting_nested_choices

    @staticmethod
    def choices_string_to_tree(choices_string):
        choices_tree = {}

        top_level_choices_list = choices_string.split('\n\n')
        top_level_choices_list = [choice.strip() for choice in top_level_choices_list]
        for top_level_choice_data in top_level_choices_list:
            indent = 0
            parent_choicedict_stack = [choices_tree]
            tag_stack = [1]

            nested_choices = choices_util.split_into_lines(top_level_choice_data)
            top_level_choice = nested_choices.pop(0)

            parent = load_choice_from_line(top_level_choice, tag_stack)

            choices_tree[parent] = {}
            current_dict = choices_tree[parent]
            # Holds the value to go back to if the next node turns out to be a leaf.
            prev_dict = choices_tree

            for choice in nested_choices:
                # Check how many spaces there are to find the indent level.
                new_indent = len(choice) - len(choice.lstrip(' '))


                if new_indent == indent:
                    current_dict = prev_dict
                elif new_indent > indent:
                    parent_choicedict_stack.append(current_dict)
                    tag_stack.append(1)
                    # If there's a same indent next, this is the level we want to be on.
                    prev_dict = current_dict
                elif new_indent < indent:
                    distance_up_stack = (indent - new_indent) // 2
                    for _ in range(distance_up_stack):
                        parent_choicedict_stack.pop()
                        tag_stack.pop()
                    current_dict = parent_choicedict_stack[-1]
                    # If there's a same indent next, this is the level we want to be on.
                    prev_dict = current_dict
                indent = new_indent

                if is_tag_marker(choice):
                    tag_stack[-1] += 1
                    continue

                choice = choice[new_indent:]
                weighted_choice = load_choice_from_line(choice, tag_stack)

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
        choices_validator.validate_choices(namespace_id, choices_string)
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
    def gen_choices(self, params={'num': 1, 'uniqueness_level': 0, 'uniqueness_mode':'each'}):
        return self._gen_choices(params)[0]

    # The same as gen_choices, but it has extra state data for internal use.
    def _gen_choices(self, params={'num': 1, 'uniqueness_level': 0, 'uniqueness_mode':'each'}):
        generated_choices = []
        # used_choices = []
        # state = {}
        choice_generator = choice_generator_mod.ChoiceGenerator(self)

        for i in range(params['num']):
            # generated = False
            # generated_choice = '$'
            # dict_and_choice_backtrace = []
            # level = 1
            choices_dict = self.choices

            generated_choice, state = choice_generator.gen_choice(choices_dict, params)
            generated_choices.append(generated_choice)

        return generated_choices, state

    def call_subtable(self, subtable_id, params):
        return self.subtables[subtable_id]._gen_choices(params)


def load_choice_from_line(line, tag_stack):
    try:
        weighted_choice = WeightedChoice(*line.split(' ', 1), tag_num=tag_stack[-1])
    except ValueError as e:
        if 'invalid literal for int() with base 10:' not in str(e):
            raise
        try:
            weight, raw_clause, choice_text = line.split('%', 2)
        except ValueError as e:
            logging.error(f'Despite not having a space, {line} doesn\'t appear to have had a state clause. That\'s is weird. I\'m also not sure how it got past the format checking.')
            raise
        logging.info(f'weight: {weight}, clause: {raw_clause}, choice_text: "{choice_text}"')
        # Choice must have a leading space now, if the format is being followed properly.
        assert choice_text[0] == ' ', f'Choice {line} seems not to have had a space following the state clause affecting the probability. This is against the format.'
        choice_text = choice_text[1:]
        # clause_list = ['%' + clause + '%' for clause in raw_clause]
        # clause_list = state_clause_handler.clause_list_from_raw_clause(raw_clause)
        clause = '%' + raw_clause + '%'
        weighted_choice = WeightedChoice(weight, choice_text, tag_num=tag_stack[-1], clause=clause)
    except TypeError:
        # Empty choice.
        weighted_choice = WeightedChoice(line, '', tag_stack[-1])

    return weighted_choice

def is_tag_marker(choice):
    return re.match('(  )+\$', choice)
if __name__ == "__main__":
    logging_level = logging.WARNING
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--info', action='store_true')
    args = parser.parse_args()
    if args.debug:
        logging_level = logging.DEBUG
    elif args.info:
        logging_level = logging.INFO
    logging.basicConfig(level=logging_level)

    choices = NestedChoices.load_from_file('test_places.txt')
    subtable = NestedChoices.load_from_string_list('countries_table', ['Germany', 'France', 'UK'], [5, 3, 1])
    choices.register_subtable(subtable)
    for choice in choices.gen_choices(params={'num': 4, 'uniqueness_level': -1}):
        print(choice)
