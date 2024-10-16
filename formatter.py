# P R O C E S S I N G   F R O M   D O C


def punctuate(input_text):
    r = input_text if input_text[-1] in ('.', '?', '!', '…') else input_text + '.'
    return r


def depunctuate(input_text):
    return input_text.rstrip('.?!…')


def capitalize(input_text):
    return input_text[0].upper() + input_text[1:]


def uncapitalize(input_text):
    return input_text[0].lower() + input_text[1:]


def ellipsize(input_text):
    return '… ' + input_text


def format_sentence(input_text):
    input_text2 = input_text.strip()
    return punctuate(capitalize(input_text2))


def format_phrase(input_text, do_capitalize=False):
    input_text2 = input_text.strip()
    return depunctuate(capitalize(input_text2)) if do_capitalize else depunctuate((uncapitalize(input_text2)))


def format_predicate(input_text):
    input_text2 = input_text.strip()
    return ellipsize(input_text2) if input_text2[0] != '…' else input_text2


def text_hash(input_text):
    text2 = input_text.strip('.?!… ')
    text2 = text2.strip()
    text2 = text2.lower()
    return text2


# T E S T

def main():
    examples = [
        "is anybody here",
        "do you smoke",
        "i woke up at 6 A.M.",
        "he visited us",
        "i visited the U.S.",

    ]
    for input_text in examples:
        print(f"Punctuation: {format_sentence(input_text)}")


if __name__ == '__main__':
    main()
