import argparse
import sys
import os
from pathlib import Path
import ezodf

import formatter
import diff

synsetid_col = 0
nid_col = 1
selector_col = 2
xselector_col = 3
text_col = 4
text0_col = 5
note_col = 6
status_col = 7
result_col = 8


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


def is_done(row):
    selector = row[selector_col].value
    xselector = row[xselector_col].value
    if selector is None or selector == '':
        v = "NOT DONE"
        row[result_col].set_value(v)
        return row


def check_text(row):
    selector = row[selector_col].value
    xselector = row[xselector_col].value
    text0 = row[text0_col].value
    text = row[text_col].value
    if text is None or text0 is None:
        # print(f'{row[synsetid_col].value} {text} {text0}', file=sys.stderr)
        return
    h0 = formatter.text_hash(text0)
    h = formatter.text_hash(text)
    if h != h0:
        d = diff.diff_substrings(h0, h)
        print(f'{row[synsetid_col].value} {d} {text0} {text}', file=sys.stderr)
        row[result_col].set_value(d)
        return row


def format(row):
    selector = row[selector_col].value
    xselector = row[xselector_col].value
    text = row[text_col].value
    if xselector == 'F':
        return
    if text is None:
        return
    if selector in ('S', 'I'):
        new_text = formatter.format_sentence(text)
        if text != new_text:
            row[result_col].set_value(new_text)
            print(f'{row[synsetid_col].value} {text}', file=sys.stderr)
            return row
    elif selector == 'P':
        new_text = formatter.format_predicate(text)
        if text != new_text:
            row[result_col].set_value(new_text)
            print(f'{row[synsetid_col].value} {text}', file=sys.stderr)
            return row
    elif selector in ('N', 'V', 'A', 'D'):
        new_text = formatter.format_phrase(text, do_capitalize=xselector == 'C')
        if text != new_text:
            row[result_col].set_value(new_text)
            print(f'{row[synsetid_col].value} {text}', file=sys.stderr)
            return row


def process_selectors(row):
    selector = row[selector_col].value
    xselector = row[xselector_col].value
    if selector is not None:
        if selector == 's':
            if xselector is not None:
                if xselector in ('i', 'I'):
                    row[result_col].set_value('I')
                    return row
                elif xselector == 's':
                    row[result_col].set_value('S')
                    return row
                else:
                    print(f'{row[synsetid_col].value} {selector} {xselector}', file=sys.stderr)
            else:
                row[result_col].set_value('S')
                return row

        elif selector == 'v':
            if xselector is not None and xselector == 'v':
                row[result_col].set_value('P')
                return row
            else:
                print(f'{row[synsetid_col].value} {selector} {xselector}', file=sys.stderr)
        elif selector == 'p':
            if xselector is not None:
                if xselector == 'v':
                    row[result_col].set_value('V')
                    return row
                elif xselector == 'n':
                    row[result_col].set_value('N')
                    return row
                elif xselector == 'a':
                    row[result_col].set_value('A')
                    return row
                elif xselector == 'd':
                    row[result_col].set_value('D')
                    return row
            else:
                print(f'{row[0].value} {selector} {xselector}', file=sys.stderr)
    else:
        id = row[0].value
        if id is not None:
            print(f'{id} {selector} {xselector}', file=sys.stderr)


def read_row(sheet):
    for row in range(sheet.nrows()):
        yield [sheet[row, col] for col in range(sheet.ncols())]


def get_processing(name):
    return globals()[name] if name else default_process


def run(filepath, processf):
    file_abspath = os.path.abspath(filepath)
    doc = ezodf.opendoc(file_abspath)
    sheet = doc.sheets[0]
    ensure_col(sheet, result_col)  # for result

    count = 0
    for row in read_row(sheet):
        new_row = processf(row)
        if new_row:
            # print(f"{'\t'.join([str(col.value) for col in new_row])}")
            # print(f"{new_row[text_col].value}")
            count += 1
    p = Path(file_abspath)
    saved = f"{p.parent}/{p.stem}_{processf.__name__}{p.suffix}"
    doc.saveas(saved)
    return count


def is_done(input):
    return input is not None and input != ""


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
