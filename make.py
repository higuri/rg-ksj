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
fs_db_name = 'area_code'
json_db_name = 'area_code.json'
cdb_name = 'area_code.cdb'

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
    elif db_type == 'cdb':
        db_name = cdb_name
    elif db_type == 'fs':
        db_name = fs_db_name
    else:
        raise ValueError()
    build_db_path = os.path.join(build_dir, db_name)
    make_db(ksj_files, db_type, build_dir, build_db_path, n_geohash)
    dist_db_path = os.path.join(dist_dir, db_name)
    # dist
    print('Making distributables...')
    os.makedirs(dist_dir)
    # - database
    shutil.move(build_db_path, dist_db_path)
    # - scripts
    shutil.copyfile(
        os.path.join(src_dir, 'query_db.py'),
        os.path.join(dist_dir, 'query_db.py'))
    shutil.copyfile(
        os.path.join(src_dir, 'geohash.py'),
        os.path.join(dist_dir, 'geohash.py'))
    if db_type == 'cdb':
        shutil.copyfile(
            os.path.join(src_dir, 'cdb.py'),
            os.path.join(dist_dir, 'cdb.py'))
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
            usage += cmd + ' build [--json, --cdb, --fs] [-n $(n_geohash)] ksj_files'
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
        (options, args) = getopt.getopt(argv[1:],
            'n:', ['json', 'cdb', 'fs'])
        for (opt, val) in options:
            if opt == '-n':
                n_geohash = int(val)
            elif opt == '--json':
                db_type = 'json'
            elif opt == '--cdb':
                db_type = 'cdb'
            elif opt == '--fs':
                db_type = 'fs'
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
        elif os.path.isfile(os.path.join(dist_dir, cdb_name)):
            from dist.query_db import get_area_from_cdb as get_area
            db_path = os.path.join(dist_dir, cdb_name)
        elif os.path.isdir(os.path.join(dist_dir, fs_db_name)):
            from dist.query_db import get_area_from_fs_db as get_area
            db_path = os.path.join(dist_dir, fs_db_name)
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
