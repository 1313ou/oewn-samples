import spacy
import sentence

nlp = spacy.load('en_core_web_sm')


def is_sentence(input_text):
    return sentence.is_sentence(input_text, nlp)


def parse_sentence(input_text):
    return sentence.parse_sentence(input_text, nlp)
