#!/usr/bin/env python3
# make_db.py

import os
import sys
from time import time
from shutil import copyfile
from .db01.make_db import make_db as make_db1
from .db02.make_db import make_db as make_db2

# make_db():
def make_db(dst_dir, ksj_files):
    db01_dir = os.path.join(dst_dir, 'db01')
    db02_dir = os.path.join(dst_dir, 'db02')

    t0 = time()

    # make_db1
    print('create database (lv.1)...')
    lat_lng_range = make_db1(ksj_files, db01_dir)
    print('copying script files for querying database (lv.1)...')
    copyfile(
        os.path.join('src', 'db01', '__init__.py'),
        os.path.join(db01_dir, '__init__.py'))
    copyfile(
        os.path.join('src', 'db01', 'query_db.py'),
        os.path.join(db01_dir, 'query_db.py'))
    copyfile(
        os.path.join('src', 'db01', 'model.py'),
        os.path.join(db01_dir, 'model.py'))

    # make_db2
    print('create database (lv.2)...')
    n_chars = 7     # 約100m弱の範囲。
    make_db2(lat_lng_range, n_chars, db02_dir, db01_dir)
    print('copying script files for querying database (lv.2)...')
    copyfile(
        os.path.join('src', 'db02', '__init__.py'),
        os.path.join(db02_dir, '__init__.py'))
    copyfile(
        os.path.join('src', 'db02', 'query_db02.py'),
        os.path.join(db02_dir, 'query_db.py'))
    copyfile(
        os.path.join('src', 'db02', 'geohash.py'),
        os.path.join(db02_dir, 'geohash.py'))

    print('Finished: %r' % (time() - t0))
    return

# main():
def main(args):
    make_db(args[0], args[1:])
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
