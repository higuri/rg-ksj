#!/usr/bin/env python3
#
# make_db.py
# - Make DB for reverse geocodeing from KSJ (Kokudo Suuchi Jouhou) files.
# [Input]
# - XML files of Kokudo Suuchi Jouhou - Administrative Boundaries
#   Data Source:
#   http://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-v2_3.html
# [Output]
# - kml/ : KML files which define polygons for administrative boundaries.
#   [Syntax]
#   kml/${pref_code}/${area_code}.kml
# - kml-index/ : index files for 'kml/'.
#   [Syntax]
#   kml-index/${lat0}/${lat1}/${lng0}/${lng1}.txt
#   -- This file contains KML file paths (polygons) which may contain
#      the coordinate (lat=${lat0}.${lat1}xxx, lng=${lng0}.${lng1}xxx).
#   e.g. kml-index/35/1/139/1.txt
#        index file for the coordinate (lat=35.1xxx, lng=139.1xxx)
#      

import sys
import os
import shutil
from .ksj2kml import make_admin_areas, make_kml_file

# get_index_file_paths():
def get_index_file_paths(polygons, index_dir):
    def fmt1(v):
        return int(v * 10)
    def fmt2(v):
        return (str(v // 10), str(v % 10))
    file_paths = set([])
    for polygon in polygons:
        r = polygon.get_range()
        minx = fmt1(r.minx)
        miny = fmt1(r.miny)
        maxx = fmt1(r.maxx)
        maxy = fmt1(r.maxy)
        for x in range(minx, maxx + 1):
            for y in range(miny, maxy + 1):
                (x0, x1) = fmt2(x)
                (y0, y1) = fmt2(y)
                fpath = os.path.join(index_dir, y0, y1, x0, x1) + '.txt'
                file_paths.add(fpath)
    return file_paths

# make_db()
def make_db(ksj_files, dst_dir='.'):
    kml_dir = os.path.join(dst_dir, 'kml')
    index_dir = os.path.join(dst_dir, 'kml-index')
    print('cleaning...')
    if os.path.isdir(kml_dir):
        shutil.rmtree(kml_dir)
    if os.path.isdir(index_dir):
        shutil.rmtree(index_dir)
    print('ready.')
    lat_lng_range = None
    for ksj_file in ksj_files:
        # parse
        print('parsing: %s...' % ksj_file)
        (admin_areas, lat_lng_range1) = make_admin_areas(ksj_file)
        if lat_lng_range is None:
            lat_lng_range = lat_lng_range1
        else:
            lat_lng_range.union(lat_lng_range1)
        # write
        for admin_area in admin_areas:
            # kml/
            ddst = os.path.join(kml_dir, admin_area.pref_code)
            if not os.path.isdir(ddst):
                os.makedirs(ddst)
            fdst = os.path.join(ddst, admin_area.id + '.kml')
            print('writing: %s...' % fdst)
            make_kml_file(admin_area, fdst)
            # kml-index/
            for fpath in get_index_file_paths(
                admin_area.bounds, index_dir):
                dirname = os.path.dirname(fpath)
                if not os.path.isdir(dirname):
                    os.makedirs(dirname)
                print('writing: %s...' % fpath)
                if os.path.isfile(fpath):
                    f = open(fpath, 'a')
                    f.write(',' + admin_area.id)
                    f.close()
                else:
                    f = open(fpath, 'w')
                    f.write(admin_area.id)
                    f.close()
    return lat_lng_range

# main()
def main(args):
    make_db(args)
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
