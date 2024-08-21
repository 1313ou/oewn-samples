import spacy
from spacy.lang.fr.tokenizer_exceptions import upper_first_letter, lower_first_letter

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


def is_sentence_simple(input_text):
    processed = nlp(input_text)
    flag = _is_sentence(processed)
    return [input_text, _deps(processed)] if flag else None


def is_sentence(input_text):
    processed = nlp(input_text)

    # Check for exactly one root
    roots = [token for token in processed if token.dep_ == "ROOT"]
    if len(roots) != 1:
        return False
    root = roots[0]

    # Check for root node
    if len(list(processed.sents)) == 0:
        return False

    # Check for nominal or clausal subject linked to the root
    subjects = [child for child in root.children if child.dep_ in {"nsubj", "nsubj:pass", "nsubjpass", "csubj"}]
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


def is_not_sentence(input_text):
    processed = nlp(input_text)
    flag = _is_sentence(processed)
    return [input_text, _deps(processed)] if not flag else None


def is_uppercase(char):
    return char.isupper()


def is_capitalized_sentence(input_text):
    processed = nlp(input_text)
    sentence_flag = _is_sentence(processed)
    capitalized_flag = is_uppercase(input_text[0])
    return [input_text, _deps(processed)] if sentence_flag and capitalized_flag else None


def is_uncapitalized_sentence(input_text):
    processed = nlp(input_text)
    sentence_flag = _is_sentence(processed)
    capitalized_flag = is_uppercase(input_text[0])
    return [input_text, _deps(processed)] if sentence_flag and not capitalized_flag else None


def capitalize_if_sentence(input_text):
    return upper_first_letter(input_text) if is_sentence(input_text) else lower_first_letter(input_text)


def main():
    examples = [
        "The quick brown fox jumps over the lazy dog.",
        "a quick brown fox",
        "running fast",
        "She loves programming and solving complex problems.",
        "The cat sat on the mat.",
        "He was smoking.",
        "this is obvious",
        "obvious though this is "
    ]
    for example in examples:
        result = is_sentence(example)
        label = "well-formed sentence" if result else "phrase"
        print(f"Text: {example}")
        print(f"Classification: {label}\n")


if __name__ == '__main__':
    main()
