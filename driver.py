import logging
import argparse
import random
import re

import random_npc
import random_shops
from nested_data import NestedChoices

HELP_TEXT = """This script generates random things. The things you can request are:
\tcharacter - Generate a random character.
\tshop - Generate a random shop.
\tgen $filename - Generates a random choice from the given file.
\ttest - Generates a random test result.
\thelp - Shows this help text.
\tquit - Quits the tool."""

def main():
    logging_level = logging.WARNING
    parser = argparse.ArgumentParser(description='Nested Choice Driver.')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    if args.debug:
        logging_level = logging.DEBUG
    logging.basicConfig(level=logging_level)

    repl()

def repl():
    command = ''
    while command != 'q' and command != 'quit':
        command = input('What do you want to generate?\n')
        command.strip()
        command = command.lower()

        if command == 'q' or command == 'quit':
            continue
        elif command == 'help':
            print(HELP_TEXT)
            continue
        elif command == 'char' or command == 'character':
            print(gen_character())
        elif command == 'shop':
            print(gen_shop())
        elif command[-5:] == ' shop':
            shop_name = command[:-5]
            logging.debug(f'custom {shop_name} shop override')
            print(gen_shop(shop_name))
        elif command == 'ushop':
            print(gen_unique_shop())
        elif command[:3] == 'gen':
            print(load_and_gen())
        else:
            print('Sorry, I didn\'t understand. Try again, or type "help" for help.')

def gen_character():
    return random_npc.create_character()

def gen_shop(shop_override=None):
    return random_shops.gen_shop(shop_override=shop_override)

def gen_unique_shop():
    return random_shops.get_unique_shop()

if __name__ == "__main__":
    main()
