#!/usr/bin/env python3
# main.py

# - build
# - clean
# - test

import tarfile
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
def build(ksj_files, n_geohash):
    def compress(src_dir, root_name, dst_file):
        with tarfile.open(dst_file, 'w:bz2') as tarbz2:
            for (root, ds, fs) in os.walk(src_dir):
                for f in fs:
                    fpath = os.path.join(root, f)
                    name = fpath[fpath.index(root_name):]
                    tarbz2.add(fpath, name)
        return
    # clean
    print('cleaning...')
    clean()
    # build
    print('ready.')
    make_db(ksj_files, build_dir, n_geohash)
    # dist
    os.makedirs(dist_dir)
    compress(
        os.path.join(build_dir, 'geohash'),
        'geohash',
        os.path.join(dist_dir, 'geohash.tar.bz2'))
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
        print(' build [-n $(n_geohash)] ksj_files')
        print(' test lat lng')
        print(' clean')
        return
    if len(argv) < 1:
        help()
        return -1
    cmd = argv[0]
    n_geohash = 7
    try:
        (options, args) = getopt.getopt(argv[1:], 'n:')
        for (opt, val) in options:
            if opt == '-n':
                n_geohash = int(val)
    except getopt.error as err:
        print(err)
        help()
        return -1
    if cmd == 'build':
        if len(args) < 1:
            help()
            return -1
        build(args, n_geohash)
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
