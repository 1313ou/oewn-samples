import sys

import spacy
from spacy.lang.fr.tokenizer_exceptions import upper_first_letter, lower_first_letter
import sentence
import question

# Load the SpaCy English model
nlp = spacy.load('en_core_web_sm')
print("loaded SpaCy", file=sys.stderr)

# P R O C E S S I N G   F R O M   D O C


def _tokens(doc):
    return [token for token in doc]


def _deps(doc):
    return [[token, token.dep_, token.pos_, token.tag_] for token in doc]


def _is_sentence(doc):
    return sentence.is_sentence(doc, nlp) is None


def _is_punctuated(doc):
    r = _tokens(doc)
    has_punctuation = any(token.dep_ in ('punct') for token in doc)
    return has_punctuation


def _is_question(doc):
    return question.is_direct_question(doc, nlp)


# P R O C E S S I N G   F U N C T I O N   F R O M   T E X T


def info(doc):
    return _deps(doc)
    #return ""


def default_process(input_text):
    return input_text


def is_sentence(input_text):
    doc = nlp(input_text)
    return _is_sentence(doc)


def is_capitalized_sentence(input_text):
    capitalized_flag = is_uppercase(input_text[0])
    return True if capitalized_flag and _is_sentence(nlp(input_text)) else None


def is_uncapitalized_sentence(input_text):
    capitalized_flag = is_uppercase(input_text[0])
    return True if not capitalized_flag and _is_sentence(nlp(input_text)) else None


def is_capitalized_nonsentence(input_text):
    capitalized_flag = is_uppercase(input_text[0])
    return True if capitalized_flag and not _is_sentence(nlp(input_text)) else None


def is_uncapitalized_nonsentence(input_text):
    capitalized_flag = is_uppercase(input_text[0])
    return True if not capitalized_flag and not _is_sentence(nlp(input_text)) else None


def capitalize_if_sentence(input_text):
    return upper_first_letter(input_text) if is_sentence(input_text) else lower_first_letter(input_text)


def is_uppercase(char):
    return char.isupper()


# T E S T

def main():
    examples = [
        "is anybody here",
        "The quick brown fox jumps over the lazy dog.",
        "a quick brown fox",
        "running fast",
        "She loves programming and solving complex problems.",
        "The cat sat on the mat.",
        "He was smoking.",
        "this is obvious",
        "obvious though this is ",
        "do you smoke",
    ]
    for input_text in examples:
        doc = nlp(input_text)
        sentence_result = _is_sentence(doc)
        question_result = _is_question(doc)
        punctuation_result = _is_punctuated(doc)

        print(f"Text: {input_text}")
        print(f"Deps: {info(doc)}")
        print(f"Sentence: {sentence_result}")
        print(f"Question: {question_result}")
        print(f"Punctuation: {punctuation_result}")
        print("\n")


if __name__ == '__main__':
    main()
