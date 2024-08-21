#!/usr/bin/python3

import wordnet_yaml
from load_process_write_yaml import process_example, process_definition
from wordnet import Example, Definition
import process
from process import *


def main():
    for data in (
    "The quick brown fox jumps over the lazy dog.",
    "the quick brown fox jumps over the lazy dog.", "A quick brown fox",
    "a quick brown fox"):
        definition = data
        print(process_definition(definition, process.capitalize_if_sentence))
        definition = Definition(data)
        print(process_definition(definition, process.capitalize_if_sentence).text)

    for data in (
    "The quick brown fox jumps over the lazy dog.",
    "the quick brown fox jumps over the lazy dog.",
    "A quick brown fox",
    "a quick brown fox"):
        example = data
        print(process_example(example, process.capitalize_if_sentence))
        example = Example(data, "source")
        print(process_example(example, process.capitalize_if_sentence).text)


if __name__ == '__main__':
    main()
