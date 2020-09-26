import random
import re

with open('custom_shops.txt', 'r', encoding='utf-8') as cs_file:
    custom_shops = cs_file.read().split('\n\n')
    custom_shops = [shop.strip() for shop in custom_shops]

with open('generic_shops.txt', 'r', encoding='utf-8') as shop_file:
    gen_shops = shop_file.read().split('\n\n')
    gen_shops = [shop.strip() for shop in gen_shops]

with open('country_places.txt', 'r', encoding='utf-8') as country_file:
    country_places = country_file.read().split('\n\n')
    country_places = [shop.strip() for shop in country_places]

with open('test_places.txt', 'r', encoding='utf-8') as test_file:
    test_places = test_file.read().split('\n\n')
    test_places = [shop.strip() for shop in test_places]

# print(country_places)

def gen_place(places):
    generated = False
    generated_place = '$'
    level = 0
    while not generated:
        weights_and_places = [place.split(' ', 1) for place in places]
        weighted_places = list(map(lambda wandp: (int(wandp[0]), wandp[1]), weights_and_places))

        total_weight = sum([i for i, _ in weighted_places])
        rand = random.randint(1, total_weight)

        i = 0
        while rand > 0:
            rand -= weighted_places[i][0]
            if rand > 0:
                i += 1
        place = weighted_places[i][1]

        if '$' not in place:
            generated_place = generated_place.replace('$', place)
            generated = True
        else:
            level += 2
            places = re.split(f'\r?\n {{{level}}}(?! )' , place)

            generated_place = generated_place.replace('$', places[0])

            places = places[1:]

    return generated_place

if __name__ == '__main__':
    print(gen_place(gen_shops))
