#!/usr/bin/python3

import os
import argparse
import sqlite3
import ezodf


def normalize(k):
    return k.strip(' .?!…;').lower().replace(",","")


def get_sample(oewnsynsetid, sampleid, conn):
    cursor = conn.cursor()
    sql = f"SELECT sample FROM samples INNER JOIN synsets USING (synsetid) WHERE oewnsynsetid = '{oewnsynsetid}' and sampleid = {sampleid}"
    cursor.execute(sql)
    return cursor.fetchone()[0]


def changed(old_sample, new_sample):
    return normalize(old_sample) == normalize(new_sample)


def create_cell_if_needed(sheet, row, col):
    current_rows = sheet.nrows()
    if current_rows <= row:
        sheet.append_rows(row - current_rows + 1)
    current_cols = sheet.ncols()
    if current_cols <= col:
        sheet.append_columns(col - current_cols + 1)
    return sheet[row, col]


def process_row(sheet, row, conn):
    synsetid_cell = sheet[row, 0]
    sampleid_cell = sheet[row, 1]
    # 2 phrase/sentence
    # 3
    new_sample_cell = sheet[row, 4]
    old_sample_cell = create_cell_if_needed(sheet, row, 5)
    compare_cell = create_cell_if_needed(sheet, row, 6)

    synsetid = synsetid_cell.value
    sampleid = sampleid_cell.value
    new_sample = new_sample_cell.value

    if synsetid is not None and sampleid is not None:
        old_sample = get_sample(synsetid, int(sampleid), conn)
        if old_sample is not None:
            old_sample_cell.set_value(old_sample)
            if new_sample is not None:
                eq = changed(old_sample, new_sample)
                if not eq:
                    compare_cell.set_value(eq)
        else:
            raise Exception(synsetid)


def process_file(file, conn):
    doc = ezodf.opendoc(file)
    sheet = doc.sheets[0]
    for row in range(sheet.nrows()):
        process_row(sheet, row, conn)
    saved = f"{os.path.dirname(file)}/{os.path.basename(file)}_with_old_example.ods"
    doc.saveas(saved)


def run(file, database):
    conn = sqlite3.connect(database)
    process_file(file, conn)
    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="update field  with sqlite database")
    parser.add_argument('file', type=str, help='data to add in csv tab-format')
    parser.add_argument('database', type=str, help='database')
    args = parser.parse_args()
    run(args.file, args.database)


if __name__ == '__main__':
    main()
