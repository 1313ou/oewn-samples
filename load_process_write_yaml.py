#!/usr/bin/python3

import argparse
import sys
import oewnio_synsets
import wordnet
import process
from process import *


def default_processing(s, synsetid):
    return s


def db_processing(s, synsetid):
    return s


do_process_definitions = False
do_process_examples = True


def process_definition(definition, synsetid, processingf):
    if isinstance(definition, str):
        definition = processingf(definition, synsetid)
    elif isinstance(definition, wordnet.Definition):
        definition.text = processingf(definition.text, synsetid)
    return definition


def process_example(example, synsetid, processingf):
    if isinstance(example, str):
        example = processingf(example, synsetid)
    elif isinstance(example, wordnet.Example):
        example.text = processingf(example.text, synsetid)
    return example


def process_synsets(wn, definition_processingf, example_processingf):
    for synset in wn.synsets:

        if do_process_definitions:
            synset.definitions = [process_definition(definition, synset.synsetid, definition_processingf) for definition in synset.definitions]

        if do_process_examples:
            if synset.examples:
                synset.examples = [process_example(example, synset.synsetid, example_processingf) for example in synset.examples]


def get_processing(name):
    return globals()[name] if name else default_processing


def main():
    parser = argparse.ArgumentParser(description="load from yaml, process and write")
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

    # read
    wn = oewnio.load(args.repo)
    print(f"loaded from {args.repo}", file=sys.stderr)
    # process
    process_synsets(wn, dprocessingf, xprocessingf)
    print("processed", file=sys.stderr)
    # write
    oewnio_synsets.save_synsets(wn, args.out)
    print(f"saved to {args.out}", file=sys.stderr)


if __name__ == '__main__':
    main()
