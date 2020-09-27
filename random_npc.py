#!/usr/bin/python

import random as rand
import math
from nested_choices import NestedChoices

def create_character(job_override=None):
  name_syllables = ['al', 'ben', 'cor', 'dan', 'fan', 'fer', 'frey', 'gra', 'gar', 'ger', 'hin', 'har',
                    'par', 'pen', 'pul', 'ser', 'star', 'ston', 'nikov', 'wray', 'chill', 'chan', 'lon',
                    'and', 'drak', 'crat', 'yon']
  name = ''.join([name_syllables[rand.randint(0, len(name_syllables)-1)] for _ in range(0, rand.randint(2, 4))])
  name = name.capitalize()

  races = ['human', 'elf', 'dwarf', 'half-elf', 'gnome', 'halfling', 'half-orc', 'orc', 'goblin']
  race_probs = [100, 10, 10, 20, 5, 5, 3, 1, 1]
  race = rand.choices(races, weights=race_probs)[0]

  gender = 'male' if rand.random() < 0.5 else 'female'

  age = math.floor(rand.gammavariate(5, 8))
  if race == 'elf':
      age *= 10
  elif race == 'dwarf':
      age *= 3
  elif race == 'goblin':
      age //= 3

  relationships = ['single', 'courting', 'engaged', 'married', 'widowed', 'divorced']
  if age < 13:
      relationship = 'single'
  elif age < 18:
      relationship = relationships[rand.randint(0, 1)]
  elif age < 25:
      relationship = relationships[rand.randint(0, 4)]
  else:
      relationship = relationships[rand.randint(0, len(relationships)-1)]

  children = 0 if relationship in ['single', 'engaged'] else min(rand.randint(0, 6), age - 18 // 2)

  jobs = ['butcher', 'baker', 'farmer', 'grocer', 'glassblower', 'blacksmith', 'tanner', 'clothier',
          'leatherworker', 'florist', 'shepherd', 'hunter', 'woodsman', 'lumberjack', 'construction worker',
          'priest', 'guard', 'guard', 'soldier', 'clerk', 'nobleman', 'barkeep', 'clockmaker', 'silversmith',
          'potter', 'cafe proprietor', 'groundskeeper', 'Dolora thug', 'Corela thug', 'Straka thug']
  nested_jobs = NestedChoices.load_from_string_list('random_jobs', jobs)
  job = nested_jobs.gen_choices()[0]

  wealths = ['dirt poor', 'dirt poor', 'poor', 'poor', 'getting by', 'getting by', 'getting by', 'well-off',
            'well-off', 'rich']
  wealth = rand.choice(wealths)

  classes = ['commoner', 'guard', 'acolyte', 'mage', 'fighter', 'ranger', 'rogue', 'bard', 'sorcerer', 'wizard']
  class_probs = [50, 25, 10, 5, 4, 2, 1, 1, 1, 1]
  npc_class = rand.choices(classes, weights=class_probs)[0]
  level = math.floor(rand.gammavariate(1, 3) + 1)

  desires = ['wealth', 'power', 'love', 'fame', 'peace and quiet', 'adventure', 'security', 'an easy life',
             'food', 'drink', 'friends', 'their family', 'revenge', 'piety', 'arcane knowledge']
  desire_probs = [100, 50, 50, 30, 100, 30, 50, 50, 30, 50, 40, 70, 10, 25, 5]
  desire = rand.choices(desires, weights=desire_probs)[0]

  event_choices = NestedChoices.load_from_file('npc_events.txt')
  event_choices.register_subtable(nested_jobs)
  events = event_choices.gen_choices(params={'num':rand.randint(1, 3), 'uniqueness_level':1})

  char = f'{name}, a {age} year(s) old {gender} {race}.\n'
  char += f'They are {relationship}, and ' + ('don\'t have' if children == 0 else f'have {children}') + ' children.\n'
  if job_override:
      char += f'They run a {job_override}'
  else:
      char += f'They are a {job}'
  char += f', and are {wealth}.\n'
  char += f'Their greatest desire in life is {desire}.\n'
  char += f'They are a level {level} {npc_class}.\n'

  for event in events:
      char += f'\n{event}.'

  return char

if __name__ == "__main__":
  print(create_character())
