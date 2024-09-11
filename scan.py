#!/usr/bin/python3

import argparse
import sqlite3
import sys
from sqlite3 import OperationalError

import read_ods


def normalize(k):
    return k.strip(' .?!…').lower()


def lookup(conn, cols):
    oewnsynsetid = cols[0]
    sampleid = str(int(cols[1]))
    sample = normalize(cols[-1].replace("'", "''"))
    cursor = conn.cursor()
    sql = f"""
    SELECT sampleid, oewnsynsetid, sample 
    FROM samples 
    LEFT JOIN synsets USING (synsetid) 
    WHERE oewnsynsetid = '{oewnsynsetid}' AND sampleid = '{sampleid}'
    """
    try:
        cursor.execute(sql)
    except OperationalError as oe:
        print(oe, sql)
    row = cursor.fetchone()
    if row is None:
        print(f"NOT FOUND {oewnsynsetid}\t{sampleid}\t{sample}\t")
    else:
        row_sample = row["sample"]
        row_sampleid = row["sampleid"]
        row_oewnsynsetid = row["oewnsynsetid"]
        if sample != row_sample:
            print(f"{row_oewnsynsetid}\t{row_sampleid}\t{row_sample}\t->\t{sample}")


def main():
    parser = argparse.ArgumentParser(description="scans the ODS")
    parser.add_argument('file', type=str, help='file')
    parser.add_argument('--col', type=int, default=-1, help='field in file to process')
    parser.add_argument('database', type=str, help='database')
    args = parser.parse_args()

    conn = sqlite3.connect(args.database)
    conn.row_factory = sqlite3.Row
    for row in read_ods.read_row(args.file):
        lookup(conn, row)
    conn.close()


if __name__ == '__main__':
    main()
