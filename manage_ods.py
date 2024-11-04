

import argparse
import sys
import os
from pathlib import Path
import ezodf

import formatter
import diff
import ods_utils
import ods_columns as col


def default_process(row):
    return row


def check_text(row):
    text0 = row[col.text0_col].value
    text = row[col.text_col].value
    if text is None or text0 is None:
        # print(f'{row[synsetid_col].value} {text} {text0}', file=sys.stderr)
        return
    h0 = formatter.text_hash(text0)
    h = formatter.text_hash(text)
    if h != h0:
        d = diff.diff_substrings(h0, h)
        print(f'{row[col.synsetid_col].value} {d} {text0} {text}', file=sys.stderr)
        row[col.diff_col].set_value(d)
        return row


def format_text(row):
    clazz = row[col.class_col].value
    directive = row[col.directive_col].value
    text = row[col.text0_col].value
    if directive == 'F':
        return
    if text is None:
        return
    if clazz in ('S', 'I'):
        new_text = formatter.format_sentence(text)
        if text != new_text:
            row[col.text_col].set_value(new_text)
            #print(f'{row[col.synsetid_col].value}\t{row[col.class_col].value}\t{row[col.directive_col].value}\t{text}')
            return row
    elif clazz == 'P':
        new_text = formatter.format_predicate(text)
        if text != new_text:
            row[col.text_col].set_value(new_text)
            #print(f'{row[col.synsetid_col].value}\t{row[col.class_col].value}\t{row[col.directive_col].value}\t{text}')
            return row
    elif clazz in ('N', 'V', 'A', 'D'):
        new_text = formatter.format_phrase(text, do_capitalize=directive == 'C')
        if text != new_text:
            row[col.text_col].set_value(new_text)
            #print(f'{row[col.synsetid_col].value}\t{row[col.class_col].value}\t{row[col.directive_col].value}\t{text}')
            return row
    else:
        raise Exception(f'unknown class {clazz}')


def read_row(sheet):
    for row in range(sheet.nrows()):
        yield [sheet[row, c] for c in range(sheet.ncols())]


def get_processing(name):
    return globals()[name] if name else default_process


def run(filepath, processf):
    file_abspath = os.path.abspath(filepath)
    doc = ezodf.opendoc(file_abspath)
    sheet = doc.sheets[0]
    ods_utils.ensure_col(sheet, col.last_col)  # for result

    count = 0
    for row in read_row(sheet):
        new_row = processf(row)
        if new_row:
            # print(f"{'\t'.join([str(c.value) for c in new_row])}")
            # print(f"{new_row[col.text_col].value}")
            count += 1
    p = Path(file_abspath)
    saved = f"{p.parent}/{p.stem}_{processf.__name__}{p.suffix}"
    doc.saveas(saved)
    return count


def main():
    parser = argparse.ArgumentParser(description="scans the ods")
    parser.add_argument('file', type=str, help='file')
    parser.add_argument('--processing', type=str, help='processing function to apply')
    args = parser.parse_args()
    processf = get_processing(args.processing)
    if processf:
        print(processf, file=sys.stderr)
    count = run(args.file, processf)
    print(f"{count} processed", file=sys.stderr)


if __name__ == '__main__':
    main()
