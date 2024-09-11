#!/usr/bin/python3

import argparse
import sys
import read_ods_map
import read_ods

def normalize(k):
    return k.strip(' .?!…;').lower().replace(",","")


def lookup(m, k):
    nk = normalize(k)
    if nk not in m:
        # raise Exception(k)
        # print(nk, file=sys.stderr)
        return None
    r = m[nk]
    return [*r, k, nk]


def main():
    parser = argparse.ArgumentParser(description="scans the csv")
    parser.add_argument('annotations', type=str, help='annotations file')
    parser.add_argument('--key', type=int, default=0, help='key column')
    parser.add_argument('--vals', type=int, default=0, nargs="+", help='value columns')
    parser.add_argument('--end', action='store_true', help='indicates the end of the list')


    parser.add_argument('data', type=str, help='data file')
    parser.add_argument('--target', type=int, default=-1, help='field to process')
    parser.add_argument('--field2', type=int, default=-1, help='field2 to process')
    args = parser.parse_args()

    m = read_ods_map.make_map(args.annotations, args.key, args.vals)
    nm = dict()
    for k in m:
        if not k:
            raise Exception(k)
        v = m[k]
        nk = normalize(k)
        nm[nk] = v
        #print(f"{k}\t{m[k]}")

    for row in read_ods.read_row(args.data):
        oewnsynsetid = row[0]
        sampleid = int(row[1])
        k = row[5]
        r = lookup(nm, k)
        if r is None:
            print(f"{oewnsynsetid}\t{sampleid}\t\t\t{k}")
            print(f"{oewnsynsetid}\t{sampleid}\t\t\t{k}", file=sys.stderr)
        else:
            print(f"{oewnsynsetid}\t{sampleid}\t{r[0]}\t{r[1]}\t{k}")

if __name__ == '__main__':
    main()
