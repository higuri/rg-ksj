#!/usr/bin/env python3
# query_db.py

import glob
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

# get_area_from_fs_db():
def get_area_from_fs_db(lat, lng, db_dir):
    if not os.path.isdir(db_dir):
        raise ValueError()
    dir1 = db_dir
    #print(encode(lat, lng, 7))
    for c in encode(lat, lng, 7):
        dir1 = os.path.join(dir1, c)
        if os.path.isdir(dir1):
            continue
        else:
            # TODO: test on windows (glob)
            files = (glob.glob(dir1 + '_*'))
            if 0 < len(files):
                assert(len(files) == 1)
                (_, area_code) = os.path.basename(files[0]).split('_')
                return area_code
            else:
                return None
    return None

# main():
def main(args):
    (lat, lng) = args[:2]
    print(get_area(float(lat), float(lng)))
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
