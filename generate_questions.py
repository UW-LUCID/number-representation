from __future__ import print_function, division

import numpy as np
import random
import pandas as pd


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
    if n in {2, 3, 5, 7, 11, 13}:
        props += ['prime']
    if n % 2 == 0:
        props += ['even']
    #  for mul in [2, 3, 5]:
        #  if n % mul == 0:
            #  props += ['{} mult'.format(mul)]
    if n in {1, 4, 9}:
        props += ['square']
    if n > 6:
        props += ['large']
    return props


def find_numbers_with_prop(prop, props):
    return {i for i in props if prop in props[i]}


def find_numbers_without_prop(prop, props):
    return {i for i in props if prop not in props[i]}


def print_csv(lines):
    filename = 'fmri-questions.csv'
    print("\n".join(lines), file=open(filename, 'w'))


def generate_questions_exploiting_properties():
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


def generate_question(a, b=-1, c=-1, n=12):
    first_loop_run = False
    while not (first_loop_run or (a != b and a != c and b != c)):
        b = np.random.randint(n) + 1
        c = np.random.randint(n) + 1
        #  print(a, b, c)
        #first_loop_run = True
    return [a, b, c]


def generate_random_queries(num_questions=192, num_targets=12):
    #  np.random.seed(42)
    assert num_questions / num_targets % 1.0 == 0.0
    repeats = num_questions / num_targets
    top_num = (np.arange(12) + 1).repeat(repeats)
    queries = [generate_question(a) for a in top_num]
    return queries


def find_number_closest_to_with_prop(n, prop, order, exclude=[]):
    props = {n: find_properties(n) for n in 1 + np.arange(12)}
    step = 1 if order == 'larger' else -1
    end = -1 if order == 'smaller' else 13
    start = n - 1 if order == 'smaller' else n + 1
    for y in range(start, end, step):
        if y in exclude:
            continue
        if y == 0 or y == 13:
            break
        if prop in props[y]:
            return y
    return False


def find_number_closest_to_without_prop(n, prop, order, exclude=[]):
    props = {n: find_properties(n) for n in 1 + np.arange(12)}
    step = 1 if order == 'larger' else -1
    end = -1 if order == 'smaller' else 13
    start = n - 1 if order == 'smaller' else n + 1
    for y in range(start, end, step):
        if y in exclude:
            continue
        if y == 0 or y == 13:
            break
        if prop not in props[y]:
            return y
    return False


def get_n_questions_with_prop(n, prop, props):
    order_a = ['smaller', 'larger', 'smaller', 'larger']
    order_b = ['smaller', 'smaller', 'larger', 'larger']
    order = list(zip(order_a, order_b))
    random.shuffle(order)
    if prop == 'large':
        pos_n = find_numbers_with_prop(prop, props) - {n}
        neg_n = find_numbers_without_prop(prop, props) - {n}
        while True:
            a = n
            b = random.choice(list(pos_n))
            c = random.choice(list(neg_n))
            if a != b and b != c and a != c:
                break
        return [a, b, c]
    for order1, order2 in order:
        a = n
        b = find_number_closest_to_with_prop(n, prop, order1)
        c = find_number_closest_to_without_prop(n, prop, order2, exclude=[b])
        if not b or not c:
            continue
        if not (a == b or b == c or a == c):
            break
    return [a, b, c]


def get_question(n, prop, props, negate=False, seed=42):
    """ n is the starting number """
    pos_n = {i: (prop in props[i]) == (prop in props[n]) for i in props}
    if negate:
        pos_n = {i: not(b) for i, b in pos_n.items()}

    # the choices we can make where they answer the question "given 4, is 2 even?"
    choices = set([i for i, v in pos_n.items() if v == True])
    choices -= {n}
    choices = np.array(list(choices))

    diffs = np.abs(choices - n)
    r = np.random.RandomState(seed)
    r.shuffle(choices)
    r = np.random.RandomState(seed)
    r.shuffle(diffs)
    to_ask = choices[np.argmin(diffs)]
    to_ask = random.choice(choices)
    return {'n': n, 'to ask': to_ask, 'property': prop,
            'match': 'no' if negate else 'yes'}


def get_questions(mean_limit=(4.0, 5.0)):
    props = {n: find_properties(n) for n in 1 + np.arange(12)}
    possible_properties = ['prime', 'large', 'even']  # , '3 mult', '5 mult']

    diffs = np.array([mean_limit[1] + 1] * 3)
    while True:
        negations = [True, False] * 6
        np.random.shuffle(negations)

        questions = [get_question(n, prop, props, negate=negate)
                     for prop in possible_properties
                     for n, negate in zip(props, negations)]

        df = pd.DataFrame(questions)

        diffs = []
        diffs_in_range = []
        for prop in ['prime', 'even', 'large']:
            temp_df = df.query('property == "{prop}"'.format(prop=prop))
            diff = np.abs(temp_df['n'] - temp_df['to ask']).mean()
            diffs_in_range += [diff > mean_limit[0] and diff < mean_limit[1]]
            diffs += [diff]

        if all(diffs_in_range):
            break
    return questions


if __name__ == "__main__":
    questions = get_questions()
    df = pd.DataFrame(questions)
    print(df)
    df.to_csv('fmri_questions.csv')


    if False:
        means = {}
        for prop in ['prime', 'even', 'large']:
            temp_df = df.query('property == "{prop}"'.format(prop=prop))
            diff = np.abs(temp_df['n'] - temp_df['to ask']).mean()
            means[prop] = diff
            means = pd.DataFrame(means_dist)
        import seaborn as sns
        import matplotlib.pyplot as plt
        for prop in means.columns:
            sns.distplot(means[prop], kde=True, label=prop)
        plt.legend(loc='best')
        plt.title('Distribution of mean distance between two numbers in question')
        plt.show()

    if False:
        df.to_csv('fmri_questions.csv')

    if False:
        queries = generate_random_queries()
        random.shuffle(queries)
        parts = [queries[len(queries)*i//4:len(queries)*(i+1)//4]
                 for i in range(4)]
        parts = np.array(parts)
        a = [{'n': q[0], 'part': i}
             for i, part in enumerate(parts)
             for q in part]

        df = pd.DataFrame(a)
        import altair
        c = altair.Chart(df).mark_bar().encode(
                x='n:N',
                y='n',
                color='part'
        )
        with open('randomness.html', 'w') as f:
            print(c.to_html(), file=f)
