import spacy
from spacy.matcher import Matcher

def _deps(doc):
    return [[token, token.dep_, token.pos_, token.tag_] for token in doc]


def _is_direct_question0(doc):
    # Get the root of the sentence
    root = [token for token in doc if token.head == token][0]

    # Check if the root is a verb and if it's in the first position
    if root.pos_ == "VERB" and root.i == 0:
        return True

    # Check for question words or auxiliary verbs at the beginning
    first_token = doc[0]
    if first_token.tag_ in ["WDT", "WP", "WP$", "WRB"] or first_token.lemma_ in ["do", "be", "have"]:
        return True

    return False


def _is_direct_question1(doc):
    # Get the root of the sentence
    root = [token for token in doc if token.head == token][0]

    # Check for subject-auxiliary inversion
    if root.pos_ == "AUX" and root.i == 0:
        return True

    # Check for question words startign sentence
    question_words = ["who", "what", "where", "when", "why", "how", "which"]
    if doc[0].lower_ in question_words:
        return True

    # Check for prepositional phrases starting with question words
    if doc[0].lower_ in ["to", "for", "with", "by", "from"]:
        if len(doc) > 1 and doc[1].lower_ in question_words:
            return True

    # Check for "do", "does", "did" followed by subject
    if doc[0].lower_ in ["do", "does", "did"] and len(doc) > 1:
        if doc[1].pos_ in ["NOUN", "PRON"]:
            return True

    # Check for modal verbs followed by subject
    modal_verbs = ["can", "could", "shall", "should", "will", "would", "may", "might", "must"]
    if doc[0].lower_ in modal_verbs and len(doc) > 1:
        if doc[1].pos_ in ["NOUN", "PRON"]:
            return True

    # Check for tag questions
    if len(doc) > 3 and doc[-3].lower_ in ["is", "are", "was", "were", "do", "does", "did", "have", "has", "had"]:
        if doc[-2].lower_ in ["it", "he", "she", "they", "we", "you", "i"] and doc[-1].lower_ in ["not", "n't"]:
            return True

    # Check if the root is a verb and if it's in the first position
    if root.pos_ == "VERB" and root.i == 0:
        return True

    # Check for question words or auxiliary verbs at the beginning
    first_token = doc[0]
    if first_token.tag_ in ["WDT", "WP", "WP$", "WRB"] or first_token.lemma_ in ["do", "be", "have"]:
        return True

    return False


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


def is_direct_question(doc, nlp):
    return _is_direct_question(doc, nlp)


def main():
    # Load the SpaCy English model
    nlp = spacy.load('en_core_web_sm')

    examples = [
        "Is this a question?",
        "What time is it?",
        "This is not a question.",
        "Can you help me?",
        "The sky is blue.",
        "To whom should I address this letter?",
        "Do you know the way to San Jose?",
        "Could I borrow your pen?",
        "You're coming to the party, aren't you?",
        "She likes ice cream, doesn't she?",
        "Why not try again?",
        "How about we go for a walk?",
        "Where did you put my keys?",
        "Have you ever been to Paris?",
        "Shall we dance?",
        "Would you mind passing the salt?",
        "Who wants ice cream?",
        "Which option do you prefer?",
        "When does the movie start?",

        "How come you didn't call?",
        "What if we tried a different approach?",
        "Could you tell me where the bathroom is?",
        "I wonder if you could help me.",
        "Do you know what time it is?",
        "Ready?",
        "Finished?",
        "Your name?",
    ]
    for input_text in examples:
        doc = nlp(input_text)
        question_result = _is_direct_question(doc, nlp)

        print(f"Text: {input_text}")
        print(f"Question: {question_result}")
        print("\n")


if __name__ == '__main__':
    main()
