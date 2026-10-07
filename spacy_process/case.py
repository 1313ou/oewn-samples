from spacy_process.lang.fr.tokenizer_exceptions import upper_first_letter, lower_first_letter
import sentence


# P R O C E S S I N G   F R O M   D O C


def _tokens(doc):
    return [token for token in doc]


def _is_punctuated(doc):
    has_punctuation = any(token.dep_ in ['punct'] for token in doc)
    return has_punctuation


def is_capitalized_sentence(doc):
    input_text = doc.input
    capitalized_flag = is_uppercase(input_text[0])
    return True if capitalized_flag and sentence._is_sentence(doc) else None


def is_uncapitalized_sentence(doc):
    input_text = doc.input
    capitalized_flag = is_uppercase(input_text[0])
    return True if not capitalized_flag and sentence._is_sentence(doc) else None


def is_capitalized_nonsentence(doc):
    input_text = doc.input
    capitalized_flag = is_uppercase(input_text[0])
    return True if capitalized_flag and not sentence._is_sentence(doc) else None


def is_uncapitalized_nonsentence(doc):
    input_text = doc.input
    capitalized_flag = is_uppercase(input_text[0])
    return True if not capitalized_flag and not sentence._is_sentence(doc) else None


def capitalize_if_sentence(doc):
    input_text = doc.input
    return upper_first_letter(input_text) if sentence._is_sentence(doc) else lower_first_letter(input_text)


def is_uppercase(char):
    return char.isupper()


def is_punctuated(input_text, nlp):
    doc = nlp(input_text)
    return _is_punctuated(doc)
