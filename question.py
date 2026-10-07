from spacy.matcher import Matcher


def _is_direct_question(doc, nlp):
    # Initialize matcher
    matcher = Matcher(nlp.vocab)

    # Check for question mark
    # if doc[-1].text == "?":
    #     return True

    # Get the root of the sentence
    root = [token for token in doc if token.head == token][0]

    # Question words and phrases
    question_words = ["who", "what", "where", "when", "why", "how", "which", "whose", "whom"]
    question_phrases = ["how come", "how about", "what if", "what about"]

    # Check for question words at the start
    if doc[0].lower_ in question_words:
        return True

    # Check for question phrases at the start
    if len(doc) > 1 and doc[0].lower_ + " " + doc[1].lower_ in question_phrases:
        return True

    # Check for prepositional phrases starting with question words
    if doc[0].pos_ == "ADP" and len(doc) > 1 and doc[1].lower_ in question_words:
        return True

    # Subject-auxiliary inversion
    if root.pos_ == "AUX" and root.i == 0:
        return True

    # Check for "do", "does", "did" followed by subject
    if doc[0].lemma_ == "do" and len(doc) > 1 and doc[1].pos_ in ["NOUN", "PRON"]:
        return True

    # Check for modal verbs followed by subject
    modal_verbs = ["can", "could", "shall", "should", "will", "would", "may", "might", "must"]
    if doc[0].lower_ in modal_verbs and len(doc) > 1 and doc[1].pos_ in ["NOUN", "PRON"]:
        return True

    # Check for tag questions
    tag_question_pattern = [
        {"LOWER": {"IN": ["is", "are", "was", "were", "do", "does", "did", "have", "has", "had", "will", "would", "can",
                          "could", "should"]}},
        {"LOWER": {"IN": ["it", "he", "she", "they", "we", "you", "i", "there", "that", "this"]}},
        {"LOWER": {"IN": ["not", "n't"]}, "OP": "?"}
    ]
    matcher.add("TAG_QUESTION", [tag_question_pattern])
    matches = matcher(doc)
    if matches and matches[-1][1] == len(doc) - 3:  # Check if the match is at the end
        return True

    # Check for indirect questions that are actually direct
    indirect_patterns = [
        [{"LOWER": "could"}, {"LOWER": "you"}, {"LOWER": "tell"}, {"LOWER": "me"}],
        [{"LOWER": "do"}, {"LOWER": "you"}, {"LOWER": "know"}],
        [{"LOWER": "i"}, {"LOWER": {"IN": ["wonder", "was", "am"]}}, {"LOWER": "wondering"}],
    ]
    for pattern in indirect_patterns:
        matcher.add("INDIRECT", [pattern])
    matches = matcher(doc)
    if matches:
        return True

    # Check for elliptical questions
    if len(doc) <= 3 and root.pos_ in ["NOUN", "ADJ", "ADV"]:
        return True

    return False


def is_direct_question(input_text, nlp):
    doc = nlp(input_text)
    return _is_direct_question(doc, nlp)
