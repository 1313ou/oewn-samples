#!/usr/bin/python3

import argparse
import sys
import oewnio
import wordnet
import wordnet_yaml
import process
from process import *


def default_processing(s):
    return s


do_process_definitions = False
do_process_examples = True


def process_definition(definition, processingf):
    if isinstance(definition, str):
        definition = processingf(definition)
    elif isinstance(definition, wordnet.Definition):
        definition.text = processingf(definition.text)
    return definition


def process_example(example, processingf):
    if isinstance(example, str):
        example = processingf(example)
    elif isinstance(example, wordnet.Example):
        example.text = processingf(example.text)
    return example


def process_synsets(wn, definition_processingf, example_processingf):
    for synset in wn.synsets:

        if do_process_definitions:
            synset.definitions = [process_definition(definition, definition_processingf) for definition in synset.definitions]

        if do_process_examples:
            if synset.examples:
                synset.examples = [process_example(example, example_processingf) for example in synset.examples]


def get_dprocessing(name):
    return globals()[name] if name else default_processing


def get_xprocessing(name):
    return globals()[name] if name else default_processing


def main():
    parser = argparse.ArgumentParser(description="load from yaml, process and write")
    parser.add_argument('repo', type=str, help='repository home')
    parser.add_argument('out', type=str, help='output dir')
    parser.add_argument('--dprocessing', type=str, help='definition processing function to apply')
    parser.add_argument('--xprocessing', type=str, help='example processing function to apply')
    args = parser.parse_args()
    dprocessingf = get_dprocessing(args.dprocessing)
    if dprocessingf:
        print(dprocessingf, file=sys.stderr)
    xprocessingf = get_xprocessing(args.xprocessing)
    if xprocessingf:
        print(xprocessingf, file=sys.stderr)

    wn = oewnio.load(args.repo)
    print(f"loaded from {args.repo}", file=sys.stderr)
    process_synsets(wn, dprocessingf, xprocessingf)
    print("processed", file=sys.stderr)
    oewnio.save(wn, args.out)
    print(f"saved to {args.out}", file=sys.stderr)


if __name__ == '__main__':
    main()
