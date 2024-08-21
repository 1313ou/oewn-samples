#!/usr/bin/python3

import wordnet_yaml
from load_process_write_yaml import process_example, process_definition
from wordnet import Example, Definition
import process
from process import *

corpus = (
    "The quick brown fox jumps over the lazy dog.",
    "the quick brown fox jumps over the lazy dog.",
    "A quick brown fox",
    "a quick brown fox",
)


def main():
    for data in corpus:
        result = process_definition(data, process.capitalize_if_sentence)
        print(f"'{data}' -> '{result}'")
        result = process_definition(Definition(data), process.capitalize_if_sentence).text
        print(f"Example('{data}') -> '{result}'")

    for data in corpus:
        result = process_example(data, process.capitalize_if_sentence)
        print(f"'{data}' -> '{result}'")
        result = process_example(Example(data, "source"), process.capitalize_if_sentence).text
        print(f"Example('{data}') -> '{result}'")


if __name__ == '__main__':
    main()
