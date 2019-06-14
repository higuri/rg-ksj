#!/usr/bin/env python3
# main.py

# - build
# - clean
# - test

import getopt
import glob
import os
import shutil
import sys
from src.make_db import make_db

build_dir = os.path.join('.', 'build')
dist_dir = os.path.join('.', 'dist')
src_dir = os.path.join('.', 'src')

# build():
def build(ksj_files, db_type, n_geohash):
    # clean
    print('Cleaning...')
    clean()
    # build
    print('Ready.')
    make_db(ksj_files, build_dir, db_type, n_geohash)
    # dist
    print('Making distributables...')
    os.makedirs(dist_dir)
    shutil.copyfile(
        os.path.join(src_dir, 'query_db.py'),
        os.path.join(dist_dir, 'query_db.py'))
    shutil.copyfile(
        os.path.join(src_dir, 'geohash.py'),
        os.path.join(dist_dir, 'geohash.py'))
    if db_type == 'json':
        shutil.copyfile(
            os.path.join(build_dir, 'area_code.json'),
            os.path.join(dist_dir, 'area_code.json'))
    elif db_type == 'fs':
        shutil.copytree(
            os.path.join(build_dir, 'area_code'),
            os.path.join(dist_dir, 'area_code'))
    return

# clean():
def clean():
    # rm build
    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir)
    # rm dist
    if os.path.isdir(dist_dir):
        shutil.rmtree(dist_dir)
    # rm *.pyc
    for dpath in glob.glob('./src/**/__pycache__', recursive=True):
        shutil.rmtree(dpath)
    for fpath in glob.glob('./src/**/*.pyc', recursive=True):
        os.remove(fpath)
    return

# main():
# TODO: specify geohash length by cmdline parameter.
def main(argv):
    def help():
        print('python3 main.py')
        print(' build [-t {json, fs}] [-n $(n_geohash)] ksj_files')
        print(' test lat lng')
        print(' clean')
        return
    if len(argv) < 1:
        help()
        return -1
    cmd = argv[0]
    db_type = 'json'
    n_geohash = 7
    try:
        (options, args) = getopt.getopt(argv[1:], 'n:t:')
        for (opt, val) in options:
            if opt == '-n':
                n_geohash = int(val)
            elif opt == '-t':
                db_type = val
    except getopt.error as err:
        print(err)
        help()
        return -1
    if cmd == 'build':
        if len(args) < 1:
            help()
            return -1
        build(args, db_type, n_geohash)
    elif cmd == 'test':
        if len(args) < 2:
            help()
            return -1
        from dist.query_db import get_area
        (lat, lng) = [float(v) for v in args[:2]]
        print(get_area(lat, lng, os.path.join(dist_dir)))
    elif cmd == 'clean':
        clean()
    else:
        raise ValueError()
    return
    
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
