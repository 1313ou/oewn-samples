import spacy

# Load the SpaCy English model
nlp = spacy.load('en_core_web_sm')


def default_process(input_text):
    return input_text


def _tokens(doc):
    return [token for token in doc]


def _deps(doc):
    return [[token,token.dep_,token.pos_] for token in doc]


def _is_sentence(doc):
    has_subject = any(token.dep_ in ('nsubj', 'nsubjpass') for token in doc)
    has_verb = any(token.pos_ in ('VERB', 'AUX') for token in doc)
    return has_subject and has_verb


def is_sentence(input_text):
    doc = nlp(input_text)
    flag = _is_sentence(doc)
    return [input_text, _deps(doc)] if flag else None


def is_not_sentence(input_text):
    doc = nlp(input_text)
    flag = _is_sentence(doc)
    return [input_text, _deps(doc)] if not flag else None


# Classify examples
def main():
    examples = [
        "The quick brown fox jumps over the lazy dog.",
        "a quick brown fox",
        "running fast",
        "She loves programming and solving complex problems."
    ]
    for example in examples:
        result = is_sentence(example)
        label = "well-formed sentence" if result else "phrase"
        print(f"Text: {example}")
        print(f"Classification: {label}\n")


if __name__ == '__main__':
    main()
