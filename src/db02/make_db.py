#!/usr/bin/env python3
# make_db.py

import multiprocessing as mp
import os
import shutil
import sys
import time
from .geohash import encode, decode
from .geohash_adjacent import get_adjacent_east, get_adjacent_north
from .query_db01 import get_area_by_geohash

# get_geohash_size()
def get_geohash_size(h):
    ((minlat, maxlat), (minlng, maxlng)) = decode(h)
    return (maxlat - minlat, maxlng - minlng)

# merge_dirs():
def merge_dirs(dir_root):
    n_merged = 0
    for (r, ds, fs) in os.walk(dir_root):
        if 0 < len(ds):
            continue
        area_codes = set([
            f.split('_')[1] for f in fs
        ])
        if 1 < len(area_codes):
            continue
        # merge
        print('merge:', r)
        shutil.rmtree(r)
        assert(len(area_codes) == 1)
        fpath = r + '_' + area_codes.pop()
        open(fpath, 'w').close()
        n_merged += 1
    return n_merged

# make_db_entries():
def make_db_entries(args): 
    (h0, n_east, db01_dir, db_path) = args
    h = h0
    t0 = time.time()
    for j in range(n_east):
        ac = get_area_by_geohash(h, db01_dir)
        if ac is not None:
            dpath = os.path.join(
                db_path , os.path.sep.join([c for c in h[:-1]]))
            fpath = os.path.join(dpath, h[-1] + '_' + ac)
            if not os.path.isdir(dpath):
                os.makedirs(dpath)
            open(fpath, 'w').close()
        # ---
        h = get_adjacent_east(h)
    print('Done: make_db_entries for (%s - %s) [%r sec]' % (
        h0, h, time.time() - t0))
    return

# make_db():
def make_db(lat_lng_range, n_chars, dst_dir, db01_dir):
    sys.path.append(os.path.join(db01_dir, '..'))
    db_path = os.path.join(dst_dir, 'geohash')
    print('cleaning...')
    if os.path.isdir(db_path ):
        shutil.rmtree(db_path )
    print('ready.')
    p0 = lat_lng_range.lower_left
    p1 = lat_lng_range.upper_right
    lower_left = encode(p0.y, p0.x, n_chars)
    lower_right = encode(p0.y, p1.x, n_chars)
    upper_left = encode(p1.y, p0.x, n_chars)
    #upper_right = encode(p1.y, p1.x, n_chars)

    # n_north / n_east
    h = lower_left
    n_north = 1
    hashes_to_north = [h]
    while h != upper_left:
        n_north += 1
        h = get_adjacent_north(h) 
        hashes_to_north.append(h)
    h = lower_left
    n_east = 1
    while h != lower_right:
        n_east += 1
        h = get_adjacent_east(h) 

    print('stat creating database...')
    print('- range: (%r, %r) to (%r, %r)' % (
        p0.lat, p0.lng, p1.lat, p1.lng))
    print('- number of cells (lat x lng): (%r x %r)' % (n_east, n_north))
    print('- cell size (lat, lng): (%r, %r)' % (get_geohash_size(h)))

    # 
    args = [(h, n_east, db01_dir, db_path) for h in hashes_to_north]
    pool = mp.Pool(mp.cpu_count())
    pool.map(make_db_entries, args)

    # merge
    while True:
        n_merged = merge_dirs(db_path )
        if n_merged == 0:
            break
    return

# main()
def main(args):
    # TODO
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
