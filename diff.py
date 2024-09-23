#!/usr/bin/python3


import difflib
import formatter


def find_diff_indexes(str1, str2):
    """
    Finds indexes where two strings differ.

    Args:
        str1 (str): The first string.
        str2 (str): The second string.

    Returns:
        list: A list of tuples, each containing the starting index and length of a substring where the strings differ.
    """
    matches = difflib.SequenceMatcher(None, str1, str2).get_matching_blocks()
    diffs = []
    for i in range(len(matches) - 1):
        start = matches[i].size
        end1 = start + matches[i].a
        end2 = start + matches[i].b
        if end1 < len(str1) and end2 < len(str2):
            d = (start, max(len(str1[end1:matches[i + 1].a]), len(str2[end2:matches[i + 1].b])) + 1)
            diffs.append(d)
    return diffs


def find_diff_substrings0(str1, str2):
    """
    Finds substrings where two strings differ.

    Args:
        str1 (str): The first string.
        str2 (str): The second string.

    Returns:
        list: A list of tuples, each containing the substring tagged with its type of change (addition, deletion, or change).
    """
    matches = difflib.SequenceMatcher(None, str1, str2).get_matching_blocks()
    diffs = []
    for i in range(len(matches) - 1):
        start = matches[i].size
        end1 = start + matches[i].a
        end2 = start + matches[i].b
        if end1 < len(str1) and end2 < len(str2):
            substring1 = str1[end1:matches[i + 1].a]
            substring2 = str2[end2:matches[i + 1].b]
            if substring1 and ' ' == substring1:
                substring1 = f"'{substring1}'"
            if substring2 and ' ' == substring2:
                substring2 = f"'{substring2}'"
            if substring1 and not substring2:
                diffs.append(f"⊖{substring1}")
            elif not substring1 and substring2:
                diffs.append(f"⊕{substring2}")
            elif substring1 != substring2:
                diffs.append(f"{substring1}→{substring2}")
    return diffs


def find_diff_substrings(str1, str2):
    """
    Finds substrings where two strings differ.

    Args:
        str1 (str): The first string.
        str2 (str): The second string.

    Returns:
        list: A list of tuples, each containing the substring and its type of change (addition, deletion, or change).
    """

    matches = difflib.SequenceMatcher(None, str1, str2).get_matching_blocks()
    diffs = []
    for i in range(len(matches) - 1):
        m = matches[i]
        l = m.size
        end1 = matches[i].a + l
        end2 = matches[i].b + l

        if end1 < len(str1) and end2 < len(str2):
            substring1 = str1[end1:matches[i + 1].a]
            substring2 = str2[end2:matches[i + 1].b]
            if substring1 and ' ' == substring1:
                substring1 = f"'{substring1}'"
            if substring2 and ' ' == substring2:
                substring2 = f"'{substring2}'"

            if substring1 and not substring2:
                diffs.append(f"⊖{substring1}")
            elif not substring1 and substring2:
                diffs.append(f"⊕{substring2}")
            elif substring1 != substring2:
                diffs.append(f"{substring1}→{substring2}")
        elif end1 < len(str1):
            diffs.append(f"⊖{str1[end1:]}")
        elif end2 < len(str2):
            diffs.append(f"⊕{str2[end2:]}")

    return diffs


def find_diff_substrings3(str1, str2):
    """
    Finds substrings where two strings differ.

    Args:
        str1 (str): The first string.
        str2 (str): The second string.

    Returns:
        list: A list of tuples, each containing the substring and its type of change (addition, deletion, or change).
    """

    diff = difflib.SequenceMatcher(None, str1, str2).get_matching_blocks()
    diff_substrings = []

    for i in range(len(diff) - 1):
        start = diff[i].size
        end1 = start + diff[i].a
        end2 = start + diff[i].b

        if end1 < len(str1) and end2 < len(str2):
            substring1 = str1[end1:diff[i + 1].a]
            substring2 = str2[end2:diff[i + 1].b]

            if substring1 and not substring2:
                diff_substrings.append(substring1 + " deletion")
            elif not substring1 and substring2:
                diff_substrings.append(substring2 + " addition")
            elif substring1 != substring2:
                if len(substring1) == 1 and len(substring2) == 1:
                    diff_substrings.append(substring1 + " " + substring2 + " change")
                else:
                    diff_substrings.append(substring1 + " " + substring2 + "change")
        elif end1 == 0:
            diff_substrings.append(str1[:diff[i + 1].a] + " deletion")
        elif end2 == 0:
            diff_substrings.append(str2[:diff[i + 1].b] + " addition")
        elif end1 == len(str1) and end2 == len(str2):
            diff_substrings.append(str1[end1:] + " " + str2[end2:] + " change")
        else:
            diff_substrings.append(str1[end1:] + " " + str2[end2:] + " change")

    return diff_substrings


def diff_indexes(str1, str2):
    return find_diff_indexes(str1, str2)


def diff_substrings(str1, str2):
    return ' / '.join(find_diff_substrings(str1, str2))


def main():
    examples = (
        ('you', 'ou'),
        ('ou', 'you'),
        ('you', 'wou'),

        ('you', 'yu'),
        ('yu', 'you'),

        ('you', 'yo'),
        ('yo', 'you'),

        ('you', 'yau'),
        ('you', 'yow')

        # (':-(and :-)', ':-( and :-)'),
        # ("is anybody here", "is anybady here"),
        # ("do you smoke", "do you smake"),
        # ("do you smoke", "do yu smake"),
        # ("do you smoke", "do you smoke"),
        # (':-(and :-) are emoticons', ':-( and :-) are emoticons'),
        # ("If we could see far into the future, …", "if we could see far into the future"),
        # ("I've had plenty, thanks (`plenty´ is nonstandard).", "(`plenty´ is nonstandard) I've had plenty, thanks"),
        # ("If you ever get married, which seems to be extremely problematic, …", "If you ever get married, which seems to be extremely problematic"),
        # ("The men cased the house.", "The men cased the housed"),
        # ("Thou art careful and troubled about many things.", ";Thou art careful and troubled about many things"),
        # ("as the saying goes, …", "as the saying goes …"),
        # ("a social gossip column", "a social gossip colum"),
        # ("If I had my way, …", "if I had my way"),
        # ("Consider the following, just as a hypothetical possibility.", "consider the following, just as a hypothetical"),
        # ("as they say in the trade, … ", "as they say in the trade"),
        # (".", "The patriciate regarded patronage of the arts as a moral and social duty.."),
    )
    for pair in examples:
        s1 = pair[0]
        s2 = pair[1]
        d = diff_substrings(formatter.text_hash(s1), formatter.text_hash(s2))
        print(f"Diff: {s1}\t{s2}\t{d}")
        # print(f"Diff: {d}")


if __name__ == '__main__':
    main()
