import numpy as np
import random
from pprint import pprint

def find_properties(n):
    props = []
    if n in {1, 3, 5, 7, 11, 13}:
        props += ['prime']
    for mul in [2, 3, 4, 5]:
        if n % mul == 0:
            props += ['{} mult'.format(mul)]
    return props

def find_numbers_with_prop(prop, props):
    return {i for i in props if prop in props[i]}
def find_numbers_without_prop(prop, props):
    return {i for i in props if prop not in props[i]}

props = {n: find_properties(n) for n in 1 + np.arange(12)}

possible_queries = {}
for a in props:
    possible_queries[a] = []
    for prop_to_test in props[a]:
        pos_n = find_numbers_with_prop(prop_to_test, props) - {a}
        neg_n = find_numbers_without_prop(prop_to_test, props) - {a}
        for b, c in zip(pos_n, neg_n):
            possible_queries[a] += [(a, b, c)]

# for n in 1 + np.arange(12):

