import argparse
import sys
import os

import ezodf
import sentence_nlp


def ensure_row(sheet, row_index):
    current_rows = sheet.nrows()
    if current_rows <= row_index:
        sheet.append_rows(row_index - current_rows + 1)


def ensure_col(sheet, col_index):
    current_cols = sheet.ncols()
    if current_cols <= col_index:
        sheet.append_columns(col_index - current_cols + 1)


def default_process(row):
    return row


def process_sentence(row):
    selector = row[2].value
    if selector is not None and selector == 's':
        input_text = row[5].value
        is_sentence, deps = sentence_nlp.parse_sentence(input_text)
        if not is_sentence:
            ensure_col(row, 6).set_value(deps)
            return row


def process_not_sentence(row):
    selector = row[2].value
    if selector is not None and selector == 'p':
        input_text = row[5].value
        is_sentence, deps = sentence_nlp.parse_sentence(input_text)
        if is_sentence:
            row[6].set_value(deps)
            return row


def read_row(sheet):
    for row in range(sheet.nrows()):
        yield [sheet[row, col] for col in range(sheet.ncols())]


def get_processing(name):
    return globals()[name] if name else default_process


def run(filename, processf):
    doc = ezodf.opendoc(filename)
    sheet = doc.sheets[0]
    ensure_col(sheet, 6) # for result
    count = 0
    for row in read_row(sheet):
        new_row = processf(row)
        if new_row:
            print(f"{'\t'.join([str(col.value) for col in new_row])}")
            count += 1
    saved = f"{os.path.dirname(filename)}/{os.path.basename(filename)}_{processf}.ods"
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
    run(args.file, processf)


if __name__ == '__main__':
    main()
