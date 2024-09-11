#!/usr/bin/python3

import argparse
import sqlite3
import ezodf

column = "status"


def get_domain(oewnsynsetid, conn):
    cursor = conn.cursor()
    sql = f"SELECT domain FROM synsets INNER JOIN domains USING (domainid) WHERE oewnsynsetid = '{oewnsynsetid}'"
    cursor.execute(sql)
    return cursor.fetchone()[0]


def process_row(sheet, row, conn):
    synsetid_cell = sheet[row, 0]
    if synsetid_cell.value is not None:
        synsetid = synsetid_cell.value
        domain = get_domain(synsetid, conn)
        if domain is not None:
            domain_cell = sheet[row, 1]
            domain_cell.set_value(domain)
        else:
            raise Exception(synsetid)


def process_file(file, conn):
    doc = ezodf.opendoc(file)
    sheet = doc.sheets[0]
    for row in range(sheet.nrows()):
        process_row(sheet, row, conn)
    doc.saveas(f"{file}_with_domain")


def run(file, database):
    conn = sqlite3.connect(database)
    process_file(file, conn)
    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="update ODS with external data from database")
    parser.add_argument('file', type=str, help='data to add in csv tab-format')
    parser.add_argument('database', type=str, help='database')
    args = parser.parse_args()
    run(args.file, args.database)


if __name__ == '__main__':
    main()
