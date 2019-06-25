#!/usr/bin/env python3
# query_db.py

import os
import sys
import json
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

# get_area_from_cdb():
def get_area_from_cdb(lat, lng, db_file):
    from .cdb import cdbget
    if not os.path.isfile(db_file):
        raise ValueError()
    hash1 = encode(lat, lng, 7)
    while 0 < len(hash1):
        try:
            return cdbget(db_file, hash1.encode()).decode()
        except KeyError:
            pass
        hash1 = hash1[:-1]
    return None

# get_area_from_fs_db():
def get_area_from_fs_db(lat, lng, db_dir):
    if not os.path.isdir(db_dir):
        raise ValueError()
    hash1 = encode(lat, lng, 7)
    while 0 < len(hash1):
        fpath1 = os.path.join(db_dir, os.path.sep.join(hash1))
        if os.path.isfile(fpath1):
            with open(fpath1) as fp:
                return fp.read()
        hash1 = hash1[:-1]
    return None

# main():
def main(args):
    (lat, lng) = args[:2]
    print(get_area(float(lat), float(lng)))
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
