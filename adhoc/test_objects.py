#!/usr/bin/python3

from utils.load_process_write_yaml import process_example, process_definition
from oewn_core.wordnet import Example

from spacy_process import case

corpus = (
    "The quick brown fox jumps over the lazy dog.",
    "the quick brown fox jumps over the lazy dog.",
    "A quick brown fox",
    "a quick brown fox",
)


def main():
    for data in corpus:
        result = process_definition(data, case.capitalize_if_sentence)
        print(f"'{data}' -> '{result}'")
        result = process_definition(Definition(data), case.capitalize_if_sentence).text
        print(f"Example('{data}') -> '{result}'")

    for data in corpus:
        result = process_example(data, case.capitalize_if_sentence)
        print(f"'{data}' -> '{result}'")
        result = process_example(Example(data, "source"), case.capitalize_if_sentence).text
        print(f"Example('{data}') -> '{result}'")


if __name__ == '__main__':
    main()
