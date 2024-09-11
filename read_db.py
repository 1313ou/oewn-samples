#!/usr/bin/python3

import argparse
import sys
import time
import sqlite3

from tqdm.auto import tqdm
import process
from process import *
import process2
from process2 import *

sql_union = """
SELECT 'sam' AS type, sampleid AS nid, sample AS `text`, oewnsynsetid FROM samples INNER JOIN synsets USING(synsetid)
UNION
SELECT 'def' AS type, synsetid AS nid, definition AS `text`, oewnsynsetid FROM synsets
"""

sql_both = f"SELECT oewnsynsetid, nid, type, `text` FROM ({sql_union}) ORDER BY oewnsynsetid, nid;"
sql_both_count = f"SELECT COUNT(*) FROM ({sql_union})"

sql_definitions = "SELECT oewnsynsetid, synsetid AS nid, 'def' AS type, definition AS `text` FROM synsets"
sql_definitions_count = "SELECT COUNT(*) FROM synsets"

sql_samples = "SELECT oewnsynsetid, sampleid AS nid, 'sam' AS type, sample AS `text` FROM samples INNER JOIN synsets USING(synsetid)"
sql_samples_count = "SELECT COUNT(*) FROM samples"

scope_2_sql = {
    None: sql_both,
    "both": sql_both,
    "definitions": sql_definitions,
    "samples": sql_samples,
}

scope_2_sql_count = {
    None: sql_both_count,
    "both": sql_both_count,
    "definitions": sql_definitions_count,
    "samples": sql_samples_count,
}


progress = False
full_print = False


def process_text(input_text, rowid, processingf):
    r = processingf(input_text)
    if r:
        if full_print:
            print(f"{rowid}\t{input_text}\t▶\t{r}")
        else:
            print(f"{rowid}\t{input_text}")
        return 1
    return 0


def count(conn, scope, resume):
    cursor = conn.cursor()
    sql2 = build_sql("count", scope, resume)
    cursor.execute(sql2)
    return cursor.fetchone()[0]


def build_sql(what, scope, resume):
    sql = scope_2_sql_count[scope] if what == "count" else scope_2_sql[scope]
    if resume:
        sql += f" WHERE oewnsynsetid >= {resume}"
    print(sql, file=sys.stderr)
    return sql


def read(file, resume, processingf, scope=None):
    conn = sqlite3.connect(file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql2 = build_sql("data", scope, resume)
    cursor.execute(sql2)
    n = count(conn, scope, resume)
    pb = tqdm(total=n, disable=not progress)
    process_count = 0
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        row_text = row["text"]
        row_nid = row["nid"]
        row_type = row["type"]
        row_oewnsynsetid = row["oewnsynsetid"]
        rowid = f"{row_oewnsynsetid}\t{row_nid}\t{row_type}"
        if process_text(row_text, rowid, processingf):
            process_count += 1
        pb.update(1)
    conn.close()
    print(f"{process_count} found/processed", file=sys.stderr)


def get_processing(name):
    return globals()[name] if name else process.default_process


def main():
    start = time.time()
    parser = argparse.ArgumentParser(description="scans the examples and definitions from sqlite file")
    parser.add_argument('database', type=str, help='database')
    parser.add_argument('--resume', type=int, help='row to resume from')
    parser.add_argument('--processing', type=str, help='processing function to apply')
    parser.add_argument('--target', type=str, help='target expr')
    parser.add_argument('--scope', type=str, help='limit to only definitions or examples')
    args = parser.parse_args()
    target = args.target
    processingf = get_processing(args.processing)
    if processingf:
        print(processingf, file=sys.stderr)
    read(args.database, args.resume, processingf, scope=args.scope)
    end = time.time()
    print(f"Duration {end - start}", file=sys.stderr)


if __name__ == '__main__':
    main()
