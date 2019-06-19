#!/usr/bin/env python3
# query_db.py

import os
import sys
import json
from zipfile import ZipFile
from .geohash import encode

# get_area_from_json_db():
def get_area_from_json_db(lat, lng, db_file):
    if not os.path.isfile(db_file):
        raise ValueError()
    hash2area = {}
    with open(db_file, 'r') as fp:
        hash2area = json.load(fp)
    hash1 = encode(lat, lng, 7)
    while 0 < len(hash1):
        if hash1 in hash2area:
            return hash2area[hash1]
        hash1 = hash1[:-1]
    return None

# get_area_from_zip_db():
def get_area_from_zip_db(lat, lng, db_file):
    if not os.path.isfile(db_file):
        raise ValueError()
    hash1 = encode(lat, lng, 7)
    with ZipFile(db_file, 'r') as zip_file:
        while 0 < len(hash1):
            entry1 = '/'.join(hash1)
            try:
                s = zip_file.read(entry1)
                return s.decode()
            except KeyError:
                pass
            hash1 = hash1[:-1]
    return None

# main():
def main(args):
    (lat, lng) = args[:2]
    print(get_area(float(lat), float(lng)))
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
