#!/usr/bin/python3

import argparse
import os
import sys
import wordnet
import ezodf
import ods_columns as cols
import wordnet_fromyaml
import wordnet_toyaml

from contextlib import contextmanager


do_process_examples = True
do_process_definitions = False


@contextmanager
def ods_map(filepath):
    file_abspath = os.path.abspath(filepath)
    doc = ezodf.opendoc(file_abspath)
    m = make_map(doc.sheets[0])
    try:
        yield m
    finally:
        m.clear()


def read_row(sheet):
    for row in range(sheet.nrows()):
        yield [sheet[row, col] for col in range(sheet.ncols())]


def make_map(sheet):
    m = dict()
    for row in read_row(sheet):
        oewnsynsetid = row[cols.synsetid_col].value
        nid = row[cols.nid_col].value
        text = row[cols.text_col].value

        if oewnsynsetid not in m:
            m[oewnsynsetid] = []
        m[oewnsynsetid].append((nid, text))
    return m


def get_example(example):
    if isinstance(example, str):
        return example
    elif isinstance(example, wordnet.Example):
        return f"{example.text} ({example.source})"


def set_example(examples, index, new_text):
    example = examples[index]
    if isinstance(example, str):
        examples[index] = new_text
    elif isinstance(example, wordnet.Example):
        example.text = new_text


def process_synset(synset, m):
    if synset.examples is None or len(synset.examples) == 0:
        # print(f"{synset.id} has no example")
        # raise Exception(f"{k} has no example")
        return 0

    k = synset.id
    if k not in m:
        print(f"model synset {k} not in data map (synset for {synset.members})")
        #raise ValueError(f"{k} has no data")
        return 0

    data = m[k]
    if not data:
        raise ValueError(f"{k} (synset for {synset.members}) has no data")

    sorted_data = sorted(data, key=lambda x: x[0])
    examples = [e[1] for e in sorted_data]
    l = len(synset.examples)
    l2 = len(examples)
    if l2 != l:
        message = f"model {synset.id} (synset for {synset.members}) and data differ in the number of examples model={l} != data={l2}"
        print(message)
        # raise ValueError(message)
    count = 0
    for i in range(l2):
        new_text = examples[i]
        set_example(synset.examples, i, new_text)
        count += 1
    return count


def process_synsets(wn, m):
    count = 0
    for synset in wn.synsets:
        count += process_synset(synset, m)
    return count


def run():
    parser = argparse.ArgumentParser(description="load from yaml, process using ods and write")
    parser.add_argument('ods', type=str, help='ods')
    parser.add_argument('repo', type=str, help='repository home')
    parser.add_argument('out_repo', type=str, help='output repo')
    args = parser.parse_args()

    # database
    with ods_map(args.ods) as m:
        print(f"map from {args.ods}", file=sys.stderr)
        # run
        print(f"loading from {args.repo}", file=sys.stderr)
        wn = wordnet_fromyaml.load(args.repo)
        print(f"loaded from {args.repo}", file=sys.stderr)
        # process
        print(f"processing", file=sys.stderr)
        n = process_synsets(wn, m)
        print(f"processed {n}", file=sys.stderr)
        # write
        print(f"saving to {args.out_repo}", file=sys.stderr)
        wordnet_toyaml.save_synsets(wn, args.out_repo)
        print(f"saved to {args.out_repo}", file=sys.stderr)


def test():
    parser = argparse.ArgumentParser(description="load from yaml, process using ods and write")
    parser.add_argument('ods', type=str, help='ods')
    parser.add_argument('repo', type=str, help='repository home')
    parser.add_argument('out_repo', type=str, help='output repo')
    args = parser.parse_args()

    # database
    with ods_map(args.ods) as m:
        print(f"map from {args.ods}", file=sys.stderr)

        # dummy synset
        synset = wordnet.Synset('00094303-n', 'n', ('m1','m2','m3'), 'lexname')
        exs = ['a', wordnet.Example('b', 'Nobody')]
        synset.examples = exs

        print('\nBefore:')
        for ex1 in synset.examples:
            print(get_example(ex1))

        process_synset(synset, m)

        print('\nAfter:')
        for ex2 in synset.examples:
            print(get_example(ex2))


def main():
    run()


if __name__ == '__main__':
    run()
