import argparse
import sys
import os
from pathlib import Path
import ezodf

import ods_utils
import ods_columns as col

import load_spacy as model
from sentence import parse_sentence

result_col = col.spacy_col
deps_col = col.spacy_deps_col


def process(row, select=None):
    nid = row[col.nid_col].value
    if not nid:
        return None
    if select is not None and not select(row):
        return None

    clazz = row[col.class_col].value
    is_tagged_sentence = clazz is not None and clazz in ('S', 'I')
    is_tagged_phrase = clazz is not None and clazz in ('P', 'N', 'V', 'A', 'D')
    if not is_tagged_sentence and not is_tagged_phrase:
        raise Exception(id)
    if not (is_tagged_sentence or is_tagged_phrase):
        raise Exception(id)

    # classify
    input_text = row[col.text_col].value
    is_sentence, deps = parse_sentence(input_text, model.nlp)
    deps = str(deps)  # .replace('\n','')

    # result
    if (is_tagged_sentence and not is_sentence) or (is_tagged_phrase and is_sentence):
        # diverge
        row[result_col].set_value('S!' if is_sentence else 'P!')
        row[deps_col].set_value(deps)
        return row
    else:
        # converge
        row[result_col].set_value('s' if is_sentence else 'p')
        row[deps_col].set_value(deps)
        return None


def process_sentence(row):
    selector = row[col.class_col].value
    return process(row, lambda r: selector is not None and selector in ('S', 'I'))


def process_not_sentence(row):
    selector = row[col.class_col].value
    return process(row, lambda r: selector is not None and selector in ('P', 'N', 'V', 'A', 'D'))


def read_row(sheet):
    for row in range(sheet.nrows()):
        yield [sheet[row, c] for c in range(sheet.ncols())]


def default_process(row):
    return row


def get_processing(name):
    return globals()[name] if name else process


def run(filepath, processf):
    file_abspath = os.path.abspath(filepath)
    doc = ezodf.opendoc(file_abspath)
    sheet = doc.sheets[0]
    ods_utils.ensure_col(sheet, col.last_col)  # for result

    count = 0
    for row in read_row(sheet):
        new_row = processf(row)
        if new_row:
            # print(f"{'\t'.join([str(col.value) for col in new_row])}")
            synsetid = row[col.synsetid_col].value
            nid = row[col.nid_col].value
            clazz = row[col.class_col].value
            print(f"{synsetid}\t{nid}\t{clazz}\t{row[col.text_col].value}\t{new_row[result_col].value.replace('\n', '')}")
            count += 1
    p = Path(file_abspath)
    saved = f"{p.parent}/{p.stem}_{processf.__name__}{p.suffix}"
    doc.saveas(saved)
    return count


def main():
    parser = argparse.ArgumentParser(description="scans the ods analyzing for sentence status")
    parser.add_argument('file', type=str, help='file')
    parser.add_argument('--processing', type=str, help='processing function to apply')
    args = parser.parse_args()
    processf = get_processing(args.processing)
    if processf:
        print(processf, file=sys.stderr)
    run(args.file, processf)


if __name__ == '__main__':
    main()
