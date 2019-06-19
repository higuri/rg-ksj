#!/usr/bin/env python3
# main.py

# - build
# - clean
# - test

import getopt
from glob import glob
import os
import shutil
import sys
from src.make_db import make_db

src_dir = os.path.join('.', 'src')
build_dir = os.path.join('.', 'build')
dist_dir = os.path.join('.', 'dist')
json_db_name = 'area_code.json'
zip_db_name = 'area_code.zip'

# build():
def build(ksj_files, db_type, n_geohash):
    # clean
    print('Cleaning...')
    clean()
    # build
    print('Ready.')
    db_name = ''
    if db_type == 'json':
        db_name = json_db_name
    elif db_type == 'zip':
        db_name = zip_db_name
    else:
        raise ValueError()
    build_db_path = os.path.join(build_dir, db_name)
    make_db(ksj_files, db_type, build_dir, build_db_path, n_geohash)
    # dist
    print('Making distributables...')
    os.makedirs(dist_dir)
    shutil.copyfile(
        build_db_path,
        os.path.join(dist_dir, db_name))
    shutil.copyfile(
        os.path.join(src_dir, 'query_db.py'),
        os.path.join(dist_dir, 'query_db.py'))
    shutil.copyfile(
        os.path.join(src_dir, 'geohash.py'),
        os.path.join(dist_dir, 'geohash.py'))
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
    for dpath in glob('./src/**/__pycache__', recursive=True):
        shutil.rmtree(dpath)
    for fpath in glob('./src/**/*.pyc', recursive=True):
        os.remove(fpath)
    return

# main():
def main(argv):
    def help(target=None):
        cmd = '\npython3 make.py'
        usage = 'Usage:'
        if target is None or target == 'build':
            usage += cmd + ' build [-t {json, zip}] [-n $(n_geohash)] ksj_files'
        if target is None or target == 'test':
            usage += cmd + ' test lat lng'
        if target is None or target == 'clean':
            usage += cmd + ' clean'
        return usage
    if len(argv) < 1:
        print(help())
        return -1
    cmd = argv[0]
    db_type = 'json'
    n_geohash = 7
    try:
        (options, args) = getopt.getopt(argv[1:], 'n:', ['json', 'zip'])
        for (opt, val) in options:
            if opt == '-n':
                n_geohash = int(val)
            elif opt == '--json':
                db_type = 'json'
            elif opt == '--zip':
                db_type = 'zip'
    except getopt.error as err:
        print(err)
        print(help())
        return -1
    if cmd == 'build':
        if len(args) < 1:
            print(help(cmd))
            return -1
        build(args, db_type, n_geohash)
    elif cmd == 'test':
        # TODO: add db spec(n_chars)
        db_path = None
        if os.path.isfile(os.path.join(dist_dir, json_db_name)):
            from dist.query_db import get_area_from_json_db as get_area
            db_path = os.path.join(dist_dir, json_db_name)
        elif os.path.isfile(os.path.join(dist_dir, zip_db_name)):
            from dist.query_db import get_area_from_zip_db as get_area
            db_path = os.path.join(dist_dir, zip_db_name)
        else:
            print('No database found. Run `build` first.')
            return -1
        if len(args) < 2:
            print(help(cmd))
            return -1
        (lat, lng) = [float(v) for v in args[:2]]
        print(get_area(lat, lng, db_path))
    elif cmd == 'clean':
        clean()
    else:   # including cmd == 'help'.
        print(help())
    return
    
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
