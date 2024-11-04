#!/usr/bin/python3

import argparse
import sqlite3
from contextlib import contextmanager

from oewn.from_yaml import load
from oewn.wordnet import Definition, Example
from oewn_core.wordnet_toyaml import save_synsets
from process import *

do_process_definitions = False
do_process_examples = True


@contextmanager
def sqlite_connection(db_name):
    conn = sqlite3.connect(db_name)
    try:
        yield conn
    finally:
        conn.close()


def db_processing(s, oewnsynsetid, conn):
    cursor = conn.cursor()
    sql = f"SELECT processed FROM samples USING (synsetid) WHERE oewnsynsetid = '{oewnsynsetid}'"
    cursor.execute(sql)
    for example, new_example in cursor.fetchall():
        if example == s:
            return new_example
    return None


def _default_processing(s, synsetid, conn):
    return s


def process_definition(definition, synsetid, processingf, conn):
    if isinstance(definition, str):
        definition = processingf(definition, synsetid, conn)
    elif isinstance(definition, Definition):
        definition.text = processingf(definition.text, synsetid, conn)
    return definition


def process_example(example, synsetid, processingf, conn):
    if isinstance(example, str):
        example = processingf(example, synsetid, conn)
    elif isinstance(example, Example):
        example.text = processingf(example.text, synsetid, conn)
    return example


def process_synsets(wn, definition_processingf, example_processingf, conn):
    for synset in wn.synsets:

        if do_process_definitions:
            synset.definitions = [process_definition(definition, synset.synsetid, definition_processingf, conn) for
                                  definition in synset.definitions]

        if do_process_examples:
            if synset.examples:
                synset.examples = [process_example(example, synset.synsetid, example_processingf, conn) for example in
                                   synset.examples]


def get_processing(name):
    return globals()[name] if name else _default_processing


def main():
    parser = argparse.ArgumentParser(description="load from yaml, process and write")
    parser.add_argument('database', type=str, help='database')
    parser.add_argument('repo', type=str, help='repository home')
    parser.add_argument('out', type=str, help='output dir')
    parser.add_argument('--dprocessing', type=str, help='definition processing function to apply')
    parser.add_argument('--xprocessing', type=str, help='example processing function to apply')
    args = parser.parse_args()
    dprocessingf = get_processing(args.dprocessing)
    if dprocessingf:
        print(dprocessingf, file=sys.stderr)
    xprocessingf = get_processing(args.xprocessing)
    if xprocessingf:
        print(xprocessingf, file=sys.stderr)

    # database
    with sqlite_connection(args.database) as conn:

        # run
        wn = load(args.repo, extend=False)
        print(f"loaded from {args.repo}", file=sys.stderr)
        # process
        process_synsets(wn, dprocessingf, xprocessingf, conn)
        print("processed", file=sys.stderr)
        # write
        save_synsets(wn, args.out)
        print(f"saved to {args.out}", file=sys.stderr)


if __name__ == '__main__':
    main()
