

import argparse
import sys
import os
from pathlib import Path
import ezodf

import ods_columns as col
import ods_utils


def default_process(row):
    return row


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
            print(f"{new_row[col.text_col].value}")
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
    run(args.file, processf)


if __name__ == '__main__':
    main()
