import numpy as np
import random


def generate(targets):
    a = random.choice(targets)
    b = random.choice(targets)
    c = random.choice(targets)
    while a == b or b == c or a == c:
        a = random.choice(targets)
        b = random.choice(targets)
        c = random.choice(targets)
    return (a, b, c)


def format_csv():
    positions = ['Center', 'Left', 'Right']
    lines = [','.join(positions + [pos + ' properties' for pos in positions])]
    for query in possible_queries:
        numbers = ['{}'.format(n) for n in query]
        properties = [' & '.join(props[n]) for n in query]
        line = ','.join(numbers) + ',' + ','.join(properties)
        lines += [line]
    return lines


def find_properties(n):
    props = []
    if n in {1, 3, 5, 7, 11, 13}:
        props += ['prime']
    for mul in [2, 3, 5]:
        if n % mul == 0:
            props += ['{} mult'.format(mul)]
    if n in {1, 4, 9}:
        props += ['square']
    return props


def find_numbers_with_prop(prop, props):
    return {i for i in props if prop in props[i]}


def find_numbers_without_prop(prop, props):
    return {i for i in props if prop not in props[i]}


def print_csv(lines):
    filename = 'fmri-questions.csv'
    print("\n".join(lines), file=open(filename, 'w'))


if __name__ == "__main__":
    props = {n: find_properties(n) for n in 1 + np.arange(12)}

    possible_queries = {}
    for a in props:
        for prop_to_test in props[a]:
            pos_n = find_numbers_with_prop(prop_to_test, props) - {a}
            neg_n = find_numbers_without_prop(prop_to_test, props) - {a}
            for b, c in zip(pos_n, neg_n):
                possible_queries = {*possible_queries, (a, b, c)}

    possible_queries = list(possible_queries)
    while len(possible_queries) != 180:
        possible_queries += [generate(list(props))]
    possible_queries += possible_queries[:20]

    lines = format_csv()
    print_csv(lines)
