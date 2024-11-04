import argparse
import os
import re
import sqlite3
import sys
from contextlib import contextmanager
from pathlib import Path
from sqlite3 import OperationalError

import ezodf

import ods_columns as col
import ods_utils


def normalize(k):
    k = re.sub(r'[,;:]', '', k)
    return (k
            .strip(' .?!…')
            .lower()
            )


# `s´ grave-acute
# ‘s’ lquote-rquote
grave = '`'
acute = '´'
lquote = '‘'
rquote = '’'


def equal_but_quotes(s1, s2):
    h1 = normalize(s1).replace(grave, '').replace(acute, '').replace(lquote, '').replace(rquote, '')
    h2 = normalize(s2).replace(grave, '').replace(acute, '').replace(lquote, '').replace(rquote, '')
    return h1 == h2


def get_data(row):
    oewnsynsetid = row[col.synsetid_col].value
    sampleid = str(int(row[col.nid_col].value))
    sample = row[col.text0_col].value
    return oewnsynsetid, sampleid, sample


def fetch_synset_samples(ods_row, conn):
    ods_oewnsynsetid, ods_sampleid, ods_sample = get_data(ods_row)
    cursor = conn.cursor()
    sql = f"""
    SELECT sampleid AS eid, oewnsynsetid, sample AS txt
    FROM samples 
    LEFT JOIN synsets USING (synsetid) 
    WHERE oewnsynsetid = '{ods_oewnsynsetid}'
    UNION
    SELECT usageid AS eid, oewnsynsetid, usagenote AS txt 
    FROM usages 
    LEFT JOIN synsets USING (synsetid) 
    WHERE oewnsynsetid = '{ods_oewnsynsetid}'
    ORDER BY eid;
    """
    try:
        cursor.execute(sql)
    except OperationalError as oe:
        print(oe, sql)
    rows = cursor.fetchall()
    if rows is None:
        print(f"\tODS NOT IN DB \t{ods_oewnsynsetid}", file=sys.stderr)
    else:
        for index, row in enumerate(rows):
            row_sample = row["txt"]
            row_sampleid = row["eid"]
            if equal_but_quotes(ods_sample, row_sample):
                print(f"\tDIFF QUOTES= {index + 1}\t{row_sampleid}\t{row_sample}")
                ods_row[col.text0_col].set_value(row_sample)
                ods_row[col.nid_col].set_value(row_sampleid)
                return ods_row

        for index, row in enumerate(rows):
            row_sample = row["txt"]
            row_sampleid = row["eid"]
            print(f"\t{index + 1}\t{row_sampleid}\t{row_sample}")


def update_from_db(ods_row, conn):
    ods_oewnsynsetid, ods_sampleid, ods_sample = get_data(ods_row)
    cursor = conn.cursor()
    escaped_sample = ods_sample.replace("'", "''")
    sql = f"""
    SELECT sampleid AS eid, oewnsynsetid, sample AS txt, 'sample' AS t
    FROM samples 
    LEFT JOIN synsets USING (synsetid) 
    WHERE oewnsynsetid = '{ods_oewnsynsetid}' AND sample = '{escaped_sample}'
    UNION
    SELECT usageid AS eid, oewnsynsetid, usagenote AS txt, 'usage' AS t
    FROM usages 
    LEFT JOIN synsets USING (synsetid) 
    WHERE oewnsynsetid = '{ods_oewnsynsetid}' AND usagenote = '{escaped_sample}';
    """
    try:
        cursor.execute(sql)
    except OperationalError as oe:
        print(oe, sql)
    row = cursor.fetchone()
    if row is None:
        print(f"NOT IN DB {ods_oewnsynsetid}\t{ods_sampleid}\t{ods_sample}\t", file=sys.stderr)
        return fetch_synset_samples(ods_row, conn)
    else:
        row_sampleid = row["eid"]
        row_oewnsynsetid = row["oewnsynsetid"]
        row_source = row["t"]
        row_sample = row["txt"]
        if ods_sampleid != row_sampleid:
            # print(f"XI={ods_oewnsynsetid}\t{ods_sampleid}\t{ods_sample}\t->\t{row_oewnsynsetid}\t{row_sampleid}")
            ods_row[col.nid_col].set_value(row_sampleid)
        ods_row[col.text0_col].set_value(row_sample)
        return ods_row


def default_process(row, conn):
    return row


def read_row(sheet):
    for row in range(sheet.nrows()):
        yield [sheet[row, c] for c in range(sheet.ncols())]


def get_processing(name):
    return globals()[name] if name else default_process


@contextmanager
def sqlite_connection(db_name):
    conn = sqlite3.connect(db_name)
    try:
        yield conn
    finally:
        conn.close()


def run(filepath, database, processf):
    with sqlite_connection(database) as conn:
        conn.row_factory = sqlite3.Row

        file_abspath = os.path.abspath(filepath)
        doc = ezodf.opendoc(file_abspath)
        sheet = doc.sheets[0]
        ods_utils.ensure_col(sheet, col.last_col)  # for result

        count = 0
        for row in read_row(sheet):
            if row and row[col.synsetid_col]:
                new_row = processf(row, conn)
                if new_row is not None:
                    # print(f"{'\t'.join([str(c.value) for c in new_row])}")
                    # print(f"{new_row[col.synsetid_col].value} {new_row[col.nid_col].value} {new_row[col.text0_col].value}")
                    count += 1

        p = Path(file_abspath)
        saved = f"{p.parent}/{p.stem}_{processf.__name__}{p.suffix}"
        doc.saveas(saved)
    return count


def main():
    parser = argparse.ArgumentParser(description="scans the ods")
    parser.add_argument('file', type=str, help='file')
    parser.add_argument('database', type=str, help='database')
    parser.add_argument('--processing', type=str, help='processing function to apply')
    args = parser.parse_args()
    processf = get_processing(args.processing)
    if processf:
        print(processf, file=sys.stderr)
    n = run(args.file, args.database, processf)
    print(f'{n} processed', file=sys.stderr)


if __name__ == '__main__':
    main()
