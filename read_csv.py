#!/usr/bin/python3

import argparse
import sys

import process
from process import *
import process2
from process2 import *


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


def read_file(file, field, processf):
    scanned = 0
    processed = 0
    with open(file) as fp:
        for line in fp:
            processed += process_line_control(line.strip(), field, processf) if field > -1 else process_line(line.strip(), processf)
            scanned += 1
    print(f"{scanned} scanned {processed} processed", file=sys.stderr)


def get_processing(name):
    return globals()[name] if name else process.default_process


def main():
    parser = argparse.ArgumentParser(description="scans the pipeline")
    parser.add_argument('file', type=str, help='file')
    parser.add_argument('--processing', type=str, help='processing function to apply')
    parser.add_argument('--field', type=int, default=-1, help='field to processs')
    args = parser.parse_args()
    processf = get_processing(args.processing)
    field = args.field
    if processf:
        print(processf, file=sys.stderr)
    read_file(args.file, field, processf)


if __name__ == '__main__':
    main()
