#!/usr/bin/python3

import argparse
import os
import sys
import oewnio
import oewnio_synsets
import wordnet
import ezodf
from contextlib import contextmanager

from oewnio_synsets import save_synsets

do_process_examples = False
do_process_examples = True

synsetid_col = 0
nid_col = 1
selector_col = 2
xselector_col = 3
text_col = 4
text0_col = 5
note_col = 6
status_col = 7
result_col = 8


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
        oewnsynsetid = row[synsetid_col].value
        nid = row[nid_col].value
        text = row[text_col].value

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
    count = 0
    if synset.examples is None or len(synset.examples) == 0:
        # print(f"{synset.id} has no example")
        # raise Exception(f"{k} has no example")
        return 0

    k = f"{synset.id[5:]}"
    if k not in m:
        print(f"{k} not in map")
        raise Exception(f"{k} has no data")
        #return 0

    data = m[k]
    if not data:
        raise Exception(f"{k} has no data")

    sorted_data = sorted(data, key=lambda x: x[0])
    examples = [e[1] for e in sorted_data]
    l = len(synset.examples)
    if len(examples) != l:
        raise Exception(f"{synset.id} and data differ in the number of examples")
    for i in range(l):
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
        wn = oewnio.load(args.repo)
        print(f"loaded from {args.repo}", file=sys.stderr)
        # process
        print(f"processing", file=sys.stderr)
        n = process_synsets(wn, m)
        print(f"processed {n}", file=sys.stderr)
        # write
        print(f"saving to {args.out_repo}", file=sys.stderr)
        oewnio_synsets.save_synsets(wn, args.out_repo)
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
        synset = wordnet.Synset('oewn-00094303-n', 'ili', 'n', 'lexname')
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
    main()
