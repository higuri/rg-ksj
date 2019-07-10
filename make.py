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

geohash2areacode_dir = 'geohash2areacode'
geohash2areacode_json = 'geohash2areacode.json'
geohash2areacode_cdb = 'geohash2areacode.cdb'
areacode2name_dir = 'areacode2name'
areacode2name_cdb = 'areacode2name.cdb'
areacode2name_json = 'areacode2name.json'

# build():
def build(ksj_files, db_type, n_geohash):
    # clean
    print('Cleaning...')
    clean()
    # build
    print('Ready.')
    make_db(ksj_files, db_type, build_dir, n_geohash)
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
        shutil.move(
            os.path.join(build_dir, geohash2areacode_json),
            os.path.join(dist_dir, geohash2areacode_json))
        shutil.move(
            os.path.join(build_dir, areacode2name_json),
            os.path.join(dist_dir, areacode2name_json))
    elif db_type == 'cdb':
        shutil.copyfile(
            os.path.join(src_dir, 'cdb.py'),
            os.path.join(dist_dir, 'cdb.py'))
        shutil.move(
            os.path.join(build_dir, geohash2areacode_cdb),
            os.path.join(dist_dir, geohash2areacode_cdb))
        shutil.move(
            os.path.join(build_dir, areacode2name_cdb),
            os.path.join(dist_dir, areacode2name_cdb))
    elif db_type == 'fs':
        shutil.move(
            os.path.join(build_dir, geohash2areacode_dir),
            os.path.join(dist_dir, geohash2areacode_dir))
        shutil.move(
            os.path.join(build_dir, areacode2name_dir),
            os.path.join(dist_dir, areacode2name_dir))
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
        gh2ac = None
        ac2an = None
        if os.path.isfile(os.path.join(dist_dir, geohash2areacode_json)):
            from dist.query_db import get_area_from_json_db as get_area
            gh2ac = os.path.join(dist_dir, geohash2areacode_json)
            ac2an = os.path.join(dist_dir, areacode2name_json)
        elif os.path.isfile(os.path.join(dist_dir, geohash2areacode_cdb)):
            from dist.query_db import get_area_from_cdb as get_area
            gh2ac = os.path.join(dist_dir, geohash2areacode_cdb)
            ac2an = os.path.join(dist_dir, areacode2name_cdb)
        elif os.path.isdir(os.path.join(dist_dir, geohash2areacode_dir)):
            from dist.query_db import get_area_from_fs_db as get_area
            gh2ac = os.path.join(dist_dir, geohash2areacode_dir)
            ac2an = os.path.join(dist_dir, areacode2name_dir)
        else:
            print('No database found. Run `build` first.')
            return -1
        if len(args) < 2:
            print(help(cmd))
            return -1
        (lat, lng) = [float(v) for v in args[:2]]
        print(get_area(lat, lng, gh2ac, ac2an))
    elif cmd == 'clean':
        clean()
    else:   # including cmd == 'help'.
        print(help())
    return
    
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
