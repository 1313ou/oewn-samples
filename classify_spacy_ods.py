import argparse
import sys
import os
from pathlib import Path
import ezodf

import sentence_spacy
import ods_utils
import ods_columns as col

result_col = col.spacy_col
deps_col = col.spacy_deps_col


def default_process(row):
    return row


def process(row, select=None):
    nid = row[col.nid_col].value
    if not nid:
        return
    if select is not None and not select(row):
        return

    clazz = row[col.class_col].value
    tagged_sentence = clazz is not None and clazz in ('S', 'I')
    tagged_phrase = clazz is not None and clazz in ('P', 'N', 'V', 'A', 'D')
    if not tagged_sentence and not tagged_phrase:
        raise Exception(id)
    if not (tagged_sentence or tagged_phrase):
        raise Exception(id)
    input_text = row[col.text_col].value
    is_sentence, deps = sentence_spacy.parse_sentence(input_text)
    deps = str(deps)  # .replace('\n','')
    if (tagged_sentence and not is_sentence) or (tagged_phrase and is_sentence):
        row[result_col].set_value('S!' if is_sentence else 'P!')
        row[deps_col].set_value(deps)
        return row
    else:
        row[result_col].set_value('s' if is_sentence else 'p')
        row[deps_col].set_value(deps)


def process_sentence(row):
    selector = row[col.class_col].value
    return process(row, lambda r: selector is not None and selector in ('S', 'I'))


def process_not_sentence(row):
    selector = row[col.class_col].value
    return process(row, lambda r: selector is not None and selector in ('P', 'N', 'V', 'A', 'D'))


def read_row(sheet):
    for row in range(sheet.nrows()):
        yield [sheet[row, c] for c in range(sheet.ncols())]


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
            print(
                f"{synsetid}\t{nid}\t{clazz}\t{row[col.text_col].value}\t{new_row[result_col].value.replace('\n', '')}")
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
