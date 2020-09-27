import random
import re

from nested_choices import NestedChoices

def gen_shop(shop_override=None):
    shop_choices = NestedChoices.load_from_file('random_shops.txt')
    if shop_override:
        override_choice = NestedChoices.load_from_string_list('generic_shops', [shop_override])
        shop_choices.register_subtable(override_choice)
    return shop_choices.gen_choices()[0]

def get_unique_shop():
    custom_shops = NestedChoices.load_from_file('custom_shops.txt')
    return custom_shops.gen_choices()[0]

if __name__ == '__main__':
    print(gen_place(gen_shops))
