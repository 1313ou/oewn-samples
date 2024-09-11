import argparse
import sys

import ezodf


def make_map(filename, key_index, values_indexes):
    doc = ezodf.opendoc(filename)
    sheet = doc.sheets[0]
    kvmap = dict()
    for rowi, row in enumerate(sheet.rows()):
        key_col = key_index
        key = sheet[rowi, key_col].value
        vals_cols = values_indexes
        vals = [sheet[rowi, val_col].value for val_col in vals_cols]
        if key:
           kvmap[key] = vals
    return kvmap


def main():
    parser = argparse.ArgumentParser(description="make a map from the ods")
    parser.add_argument('file', type=str, help='file')
    parser.add_argument('--key', type=int, default=0, help='key column')
    parser.add_argument('--vals', type=int, default=0, nargs="+", help='value columns')
    parser.add_argument('--end', action='store_true', help='indicates the end of the list')
    args = parser.parse_args()
    return make_map(args.file, args.key, args.vals)


if __name__ == '__main__':
    m = main()
    for k in m:
        print(f"{k}\t{m[k]}")
