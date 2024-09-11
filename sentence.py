import spacy
from spacy.lang.fr.tokenizer_exceptions import upper_first_letter, lower_first_letter


# P R O C E S S I N G   F R O M   D O C


def _is_sentence0(doc):
    has_subject = any(token.dep_ in ('nsubj', 'nsubjpass') for token in doc)
    has_verb = any(token.pos_ in ('VERB', 'AUX') for token in doc)
    return has_subject and has_verb


def _is_sentence(doc):
    # Check for exactly one root
    roots = [token for token in doc if token.dep_ == "ROOT"]
    if len(roots) != 1:
        return False
    root = roots[0]

    # Check for root node
    if len(list(doc.sents)) == 0:
        return False

    # Check for nominal or clausal subject linked to the root
    subjects = [child for child in root.children if child.dep_ in {"nsubj", "nsubj:pass", "nsubjpass", "csubj", "attr"}]
    if not subjects:
        return False

    # Ensure the root is a verb or copula
    if root.pos_ not in {"VERB", "AUX"}:
        return False

    # Ensure appropriate punctuation at the end of the sentence
    # if processed[-1].dep_ != "punct":
    #     return False

    # Check for no cycles and proper tree structure
    def check_tree_structure(token, visited):
        if token in visited:
            return False
        visited.add(token)
        for child in token.children:
            if not check_tree_structure(child, visited):
                return False
        return True

    if not check_tree_structure(root, set()):
        return False

    # Ensure basic sentence structures are present
    # has_object_or_complement = any(child.dep_ in {"obj", "iobj", "ccomp", "xcomp"} for child in root.children)
    # if not has_object_or_complement:
    #     return False

    return True


# P R O C E S S I N G   F U N C T I O N   F R O M   T E X T
# returns none if sentence else doc

def _deps(doc):
    return [[token, token.dep_, token.pos_, token.tag_] for token in doc]


def is_sentence(input_text, nlp):
    doc = nlp(input_text)
    return _is_sentence(doc)


def parse_sentence(input_text, nlp):
    doc = nlp(input_text)
    flag = _is_sentence(doc)
    return flag, _deps(doc)


# T E S T

def main():
    # Load the SpaCy English model
    nlp = spacy.load('en_core_web_sm')

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

        print(f"Text: {input_text}")
        print(f"Deps: {_deps(doc)}")
        print(f"Sentence: {sentence_result}")
        print("\n")


if __name__ == '__main__':
    main()
