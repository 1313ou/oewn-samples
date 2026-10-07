#!/usr/bin/python3

import argparse
import sys


def process_line(line, processf):
    fields = line.split('\t')
    last = len(fields) - 1
    input_text = fields[last]
    rowid = "\t".join(fields[0:last])
    r = processf(input_text)
    if r:
        # print(f"{rowid}\t{r}\t{input_text}")
        print(f"{rowid}\t{r}")
        return 1
    return 0


def process_line_control(line, target, processf):
    fields = line.split('\t')
    input = fields[target]
    r = processf(input)
    if r:
        # print(f"{rowid}\t{r}\t{input_text}")
        last = len(fields) - 1
        rowid = "\t".join(fields[0:last])
        print(f"{rowid}\t{r}")
        return 1
    return 0


def process_line_accumulate(line, target, processf, m):
    fields = line.split('\t')
    input = fields[target]
    r = processf(input)
    if r:
        if r in m:
            print(f"duplicate {r}", file=sys.stderr)
            #raise Exception(r)
        # print(f"{rowid}\t{r}\t{input_text}")
        last = len(fields) - 1
        #rowid = "\t".join(fields[0:last])
        m[r] = fields[0:last]
        return 1
    return 0


def read_file(file, field, processf):
    scanned = 0
    processed = 0
    idmap = dict()
    with open(file) as fp:
        for line in fp:
            processed += process_line_accumulate(line.strip(), field, processf, idmap) if field > -1 else process_line(line.strip(), processf)
            scanned += 1
    print(f"{scanned} scanned {processed} processed", file=sys.stderr)
    return idmap


def make_map(file, field, processf):
    return read_file(file, field, processf)


def get_processing(name):
    return globals()[name] if name else lambda x : x


def main():
    parser = argparse.ArgumentParser(description="scans the csv")
    parser.add_argument('file', type=str, help='file')
    parser.add_argument('--processing', type=str, help='processing function to apply')
    parser.add_argument('--field', type=int, default=-1, help='field to processs')
    args = parser.parse_args()
    processf = get_processing(args.processing)
    field = args.field
    if processf:
        print(processf, file=sys.stderr)
    m = make_map(args.file, field, processf)
    for k in m:
        print(f"{k}\t{m[k]}")


if __name__ == '__main__':
    main()
