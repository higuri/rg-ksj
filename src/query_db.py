#!/usr/bin/env python3
# query_db.py

import glob
import os
import sys
from .geohash import encode

# get_area():
def get_area(lat, lng, db_root='build'):
    path = os.path.join(db_root, 'geohash')
    if not os.path.isdir(path):
        raise ValueError()
    #print(encode(lat, lng, 7))
    for c in encode(lat, lng, 7):
        path = os.path.join(path, c)
        if os.path.isdir(path):
            continue
        else:
            # TODO: test on windows (glob)
            files = (glob.glob(path + '_*'))
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
