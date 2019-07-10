#!/usr/bin/env python3
# query_db.py

import os
import sys
import json
from .geohash import encode

# get_area_from_json_db():
def get_area_from_json_db(lat, lng, gh2ac_path, ac2an_path):
    if not os.path.isfile(gh2ac_path) or not os.path.isfile(ac2an_path):
        raise ValueError()
    # gh2ac
    area_code = None
    gh2ac = {}
    with open(gh2ac_path, 'r') as fp:
        gh2ac = json.load(fp)
    gh1 = encode(lat, lng, 7)
    while 0 < len(gh1):
        if gh1 in gh2ac:
            area_code = gh2ac[gh1]
            break;
        gh1 = gh1[:-1]
    del gh2ac
    # ac2an
    if area_code is not None:
        ac2an = {}
        with open(ac2an_path, 'r') as fp:
            ac2an = json.load(fp)
        if area_code in ac2an:
            return ac2an[area_code]
    return None

# get_area_from_cdb():
def get_area_from_cdb(lat, lng, gh2ac_path, ac2an_path):
    from .cdb import cdbget
    if not os.path.isfile(gh2ac_path) or not os.path.isfile(ac2an_path):
        raise ValueError()
    # gh2ac
    area_code = None
    gh1 = encode(lat, lng, 7)
    while 0 < len(gh1):
        try:
            area_code = cdbget(gh2ac_path, gh1)
            break
        except KeyError:
            pass
        gh1 = gh1[:-1]
    # ac2an
    if area_code is not None:
        try:
            area_name = cdbget(ac2an_path, area_code)
            return area_name
        except KeyError:
            pass
    return None

# get_area_from_fs_db():
def get_area_from_fs_db(lat, lng, gh2ac_path, ac2an_path):
    if not os.path.isdir(gh2ac_path) or not os.path.isdir(ac2an_path):
        raise ValueError()
    gh1 = encode(lat, lng, 7)
    while 0 < len(gh1):
        fpath1 = os.path.join(gh2ac, os.path.sep.join(gh1))
        if os.path.isfile(fpath1):
            with open(fpath1) as fp:
                return fp.read()
        gh1 = gh1[:-1]
    return None

# main():
def main(args):
    (lat, lng) = args[:2]
    print(get_area(float(lat), float(lng)))
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
