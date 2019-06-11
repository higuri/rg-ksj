#!/usr/bin/env python3
# main.py

# - build
# - clean
# - test

import glob
import os
import shutil
import sys
from src.make_db import make_db

build_dir = os.path.join('.', 'build')
dist_dir = os.path.join('.', 'dist')

# build():
def build(ksj_files):
    print('cleaning...')
    clean()
    print('ready.')
    # make build
    make_db(build_dir, ksj_files)
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
def main(args):
    cmd = args[0]
    if cmd == 'build':
        build(args[1:])
    elif cmd == 'clean':
        clean()
    elif cmd == 'test':
        # TODO
        pass
    else:
        raise ValueError()
    return
    
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
