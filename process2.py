
# P R O C E S S I N G   F R O M   D O C

def is_uppercase(char):
    return char.isupper()


def capitalize_punctuate(input_text):
    input_text2 = input_text.strip()
    input_text2 = input_text2[0].upper() + input_text2[1:]
    return input_text2 if input_text2[-1] in ('.', '?', '!') else input_text2 + '.'


def capitalize_punctuate_if_sentence(input_text):
    input_text2 = input_text.strip()
    input_text2 = input_text2[0].upper() + input_text2[1:]
    return input_text2 if input_text2[-1] in ('.', '?', '!') else input_text2 + '.'


def is_done(input):
    return input is not None and input != ""


# T E S T

def main():
    examples = [
        "is anybody here",
        "do you smoke",
    ]
    for input_text in examples:
        print(f"Punctuation: {capitalize_punctuate(input_text)}")
        print("\n")


if __name__ == '__main__':
    main()
