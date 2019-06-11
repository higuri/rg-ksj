#!/usr/bin/env python3
#
# db01/make_db.py
# - Make DB for reverse geocodeing from KSJ (Kokudo Suuchi Jouhou) files.
# [Input]
# - XML files of Kokudo Suuchi Jouhou - Administrative Boundaries
#   Data Source:
#   http://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-v2_3.html
# [Output]
# - kml/ : KML files which define polygons of administrative boundaries.
#   [Syntax]
#   kml/${pref_code}/${area_code}.kml
# - kml-index/ : index files for 'kml/',
#                for improving search efficiency.
#   [Syntax]
#   kml-index/${lat0}/${lat1}/${lng0}/${lng1}.txt
#   *) This file contains KML file paths (polygons) which may contain
#      the coordinate (lat=${lat0}.${lat1}xxx, lng=${lng0}.${lng1}xxx).
#      e.g. kml-index/35/1/139/1.txt:
#           The index file for the coordinate (lat=35.1xxx, lng=139.1xxx)
#      

import os
import sys
import shutil
from time import time
import multiprocessing as mp
import re
import sys
import xml.etree.ElementTree as ET
# from .model import Point, Polygon
from shapely.geometry import Point, Polygon
from .geohash import encode, decode, get_longest_geohash, get_sub_geohashes

## XML Namespaces used in KML.
KML_NS = {
    'kml': 'http://www.opengis.net/kml/2.2'
}
## XML Namespaces used in GML for KSJ (Kokudo Suuchi Jouho).
KSJ_NS = {
    'gml': 'http://www.opengis.net/gml/3.2',
    'ksj': 'http://nlftp.mlit.go.jp/ksj/schemas/ksj-app',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'xlink': 'http://www.w3.org/1999/xlink'
}

# get_area_code():
def get_area_code(kml_file):
    return os.path.splitext(os.path.basename(kml_file))[0]

# make_polygons(): kml_file -> [(polygon, lat_lng_range),...]
def make_polygons(kml_file):
    def parse_coords_lines(lines):
        points = []
        minlat = maxlat = minlng = maxlng = None
        for line in lines.splitlines():
            s = line.strip()
            if 0 < len(s):
                (lng, lat) = [float(v) for v in s.split(',')]
                if minlat is None:
                    minlat = maxlat = lat
                    minlng = maxlng = lng
                else:
                    if lat < minlat: minlat = lat
                    if maxlat < lat: maxlat = lat
                    if lng < minlng: minlng = lng
                    if maxlng < lng: maxlng = lng
                points.append((lat, lng))
        return (Polygon(points), ((minlat, maxlat), (minlng, maxlng)))
    retval = []
    tree = ET.parse(kml_file)
    root = tree.getroot()
    kml_doc = root.find('kml:Document', KML_NS)
    for placemark in kml_doc.findall('kml:Placemark', KML_NS):
        for polygon in placemark.findall('kml:Polygon', KML_NS):
            bounds = polygon.find('kml:outerBoundaryIs', KML_NS)
            ring = bounds.find('kml:LinearRing', KML_NS)
            coords = ring.find('kml:coordinates', KML_NS)
            (polygon, lat_lng_range) = parse_coords_lines(coords.text)
            retval.append((polygon, lat_lng_range))
    return retval

# make_kml_file(): [polygon] -> kml_file
def make_kml_file(polygons, title, dst_file):
    f = open(dst_file, 'w')
    f.write('<?xml version="1.0" encoding="utf-8" standalone="no"?>\n')
    f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    f.write('<Document>\n')
    f.write('<name>%s</name>\n' % (title))
    for (i, polygon) in enumerate(polygons):
        f.write('<Placemark id="%d">\n' % (i+1))
        f.write('<name>%d</name>\n' % (i+1))
        f.write('<Polygon>\n')
        f.write('<outerBoundaryIs>\n')
        f.write('<LinearRing>\n')
        f.write('<coordinates>\n')
        for (lat, lng) in polygon.exterior.coords:
            f.write(' %s,%s\n' % (lng, lat))
        f.write('</coordinates>\n')
        f.write('</LinearRing>\n')
        f.write('</outerBoundaryIs>\n')
        f.write('</Polygon>\n')
        f.write('</Placemark>\n')
    f.write('</Document>\n')
    f.write('</kml>\n')
    f.close()
    return

# make_sfid2cvids_dict():
def make_sfid2cvids_dict(etree_root):
    sfid2cvids = {}
    for surface in etree_root.findall('gml:Surface', KSJ_NS):
        surface_id = surface.get('{%s}id' % KSJ_NS['gml'])
        patches = surface.find('gml:patches', KSJ_NS)
        patch = patches.find('gml:PolygonPatch', KSJ_NS)
        exterior = patch.find('gml:exterior', KSJ_NS)
        # TODO: interior
        ring = exterior.find('gml:Ring', KSJ_NS)
        curveMember = ring.find('gml:curveMember', KSJ_NS)
        curveRef = curveMember.get('{%s}href' % KSJ_NS['xlink'])
        curve_id = curveRef.replace('#', '')
        sfid2cvids[surface_id] = [curve_id]
    return sfid2cvids

# make_areacode2sfids_dict():
def make_areacode2sfids_dict(etree_root):
    areacode2sfids = {}
    areacode2areaname = {}
    for boundary in etree_root.findall('ksj:AdministrativeBoundary', KSJ_NS):
        bounds = boundary.find('ksj:bounds', KSJ_NS)
        boundsRef = bounds.get('{%s}href' % KSJ_NS['xlink'])
        surface_id = boundsRef.replace('#', '')
        e0 = boundary.find('ksj:administrativeAreaCode', KSJ_NS)
        e1 = boundary.find('ksj:prefectureName', KSJ_NS)
        e2 = boundary.find('ksj:cityName', KSJ_NS)
        if (e0 is None or e1 is None or e2 is None):
            continue
        if (e0.text is None or e1.text is None or e2.text is None):
            # area code of '所属未定地' is None.
            continue
        area_code = e0.text.strip()
        pref_name = e1.text.strip()
        city_name = e2.text.strip()
        # areacode2sfids
        if area_code not in areacode2sfids:
            areacode2sfids[area_code] = []
        areacode2sfids[area_code].append(surface_id)
        # areacode2areaname
        if area_code not in areacode2areaname:
            areacode2areaname[area_code] = '%s,%s' % (pref_name, city_name)
    return (areacode2sfids, areacode2areaname)

# make_curve_files_from_etree():
def make_curve_files_from_etree(etree_root, get_curve_fpath):
    # make_polygon():
    def make_polygon(pos_list_text):
        points = []
        for line in pos_list_text.splitlines():
             s = line.strip()
             if 0 < len(s):
                (lat, lng) = [float(v) for v in s.split(' ')]
                points.append((lat, lng))
        # 閉じられていること。
        # assert(points[0].is_same_coordinate(points[-1]))
        return Polygon(points)
    for curve in etree_root.findall('gml:Curve', KSJ_NS):
        curve_id = curve.get('{%s}id' % KSJ_NS['gml'])
        segments = curve.find('gml:segments', KSJ_NS)
        segment = segments.find('gml:LineStringSegment', KSJ_NS)
        posList = segment.find('gml:posList', KSJ_NS)
        polygon = make_polygon(posList.text)
        fpath = get_curve_fpath(curve_id)
        if not os.path.isdir(os.path.dirname(fpath)):
            os.makedirs(os.path.dirname(fpath))
        make_kml_file([polygon], curve_id, fpath)
    return

# make_curve_files():
def make_curve_files(ksj_file, dst_dir):
    # get_curve_fpath():
    CURVE_ID_PAT = re.compile(r'cv([0-9]+)_[0-9]+')
    def get_curve_fpath(curve_id):
        m = CURVE_ID_PAT.match(curve_id)
        assert(m is not None)
        i = int(m.group(1))
        # max 1000 files / directory (for debuggability).
        dpath = os.path.join(dst_dir, str(i // 1000))
        return os.path.join(dpath, curve_id + '.kml')
    etree_root = ET.parse(ksj_file).getroot()
    # ksj(etree) -> curve files (.kml)
    make_curve_files_from_etree(etree_root, get_curve_fpath)
    # ksj(etree) -> {surface_id: [curve_id]}
    sfid2cvids = make_sfid2cvids_dict(etree_root)
    (areacode2sfids, areacode2areaname) = make_areacode2sfids_dict(etree_root)
    areacode2curvefiles = {}
    for (area_code, surface_ids) in areacode2sfids.items():
        areacode2curvefiles[area_code] = []
        for surface_id in surface_ids:
            # surface_id -> curve_id
            for curve_id in sfid2cvids[surface_id]:
                # curve_id -> curve file path
                fpath = get_curve_fpath(curve_id)
                areacode2curvefiles[area_code].append(fpath)
    return areacode2curvefiles

# make_kml_files():
# dst_dir: 'kml/' - contains KML files which define
#          polygons of administrative boundaries.
def make_kml_files(ksj_file, dst_dir):
    # tmpdir: 'tmp/' - contains KML files which define
    #          polygons of administrative boundary fragments
    #          (Curve objects in KSJ).
    # (*) We write out boundary fragments,
    #     that are read from a KSJ file, to (KML) files
    #     in order to parse large KSJ file
    #     even on machines that don't have enough memory.
    #     e.g. N03-18_180101.xml: 500MB
    #          contains administrative areas of whole of Japan.
    tmp_dir = os.path.join(dst_dir, 'tmp')
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
    ##
    # ksj_file -> {area_code: [curve_file(.kml)...]}
    #   write out ksj:Curve objects (boundary fragments) to KML files.
    areacode2curvefiles = make_curve_files(ksj_file, tmp_dir)
    for (area_code, curve_files) in areacode2curvefiles.items():
        polygons = []
        # curve_file -> [polygon...]
        for curve_file in curve_files:
            polygons += [
                polygon for (polygon, _ ) in make_polygons(curve_file)
            ]
        # kml/: [polygon...] -> .kml
        pref_code = area_code[:2]
        pref_dir = os.path.join(dst_dir, pref_code)
        if not os.path.isdir(pref_dir):
            os.makedirs(pref_dir)
        kml_path = os.path.join(pref_dir, area_code + '.kml')
        print('writing: %s...' % kml_path)
        make_kml_file(polygons, area_code, kml_path)
    shutil.rmtree(tmp_dir)
    return

# make_db01():
def make_db01(ksj_files, n_chars, dst_dir='.'):
    # db01
    kml_dir = os.path.join(dst_dir, 'kml')
    for ksj_file in ksj_files:
        # parse
        print('reading: %s...' % ksj_file)
        make_kml_files(ksj_file, kml_dir)
    # db02
    geohash_dir = os.path.join(dst_dir, 'geohash')
    make_db02(kml_dir, n_chars, geohash_dir)
    return


#####  db02

# write_db_entry()
def write_db_entry(geohash, area_code, geohash_dir):
    dpath = os.path.join(
        geohash_dir, os.path.sep.join([c for c in geohash[:-1]]))
    fpath = os.path.join(dpath, geohash[-1] + '_' + area_code)
    if not os.path.isdir(dpath):
        os.makedirs(dpath)
    #print("writing: %s..." % fpath)
    open(fpath, 'w').close()
    return

# make_db_entries():
def make_db_entries(args): 
    (kml_file, n_chars, geohash_dir) = args
    area_code = get_area_code(kml_file)
    #
    def make_polygon(lat_lng_range):
        ((minlat, maxlat), (minlng, maxlng)) = lat_lng_range
        return Polygon([
            (minlat, minlng),
            (minlat, maxlng),
            (maxlat, maxlng),
            (maxlat, minlng),
            (minlat, minlng)
        ])
    #
    def make_point(lat_lng_range):
        ((minlat, maxlat), (minlng, maxlng)) = lat_lng_range
        return Point((minlat + maxlat) / 2, (maxlat + maxlng) / 2)
    #
    def doit(geohash, polygon):
        for (geohash1, range1) in get_sub_geohashes(geohash):
            polygon1 = make_polygon(range1)
            if polygon.intersects(polygon1):
                if polygon.contains(polygon1):
                    write_db_entry(geohash1, area_code, geohash_dir)
                elif len(geohash1) < n_chars:
                    doit(geohash1, polygon)
                else:
                    center = make_point(range1)
                    if polygon.contains(center):
                        write_db_entry(geohash1, area_code, geohash_dir)
            else:
                # polygon1 is outside of polygon.
                pass    # nop
        return
    #
    print('parsing: %s...' % kml_file)
    for (polygon, lat_lng_range) in make_polygons(kml_file):
        geohash = get_longest_geohash(lat_lng_range, n_chars)
        if len(geohash) < n_chars:
            doit(geohash, polygon)
        else:
            # Okinotori case?
            write_db_entry(geohash, area_code, geohash_dir)
    return

# make_db02():
def make_db02(kml_dir, n_chars, dst_dir):
    kml_files = []
    for (root, dirs, files) in os.walk(kml_dir):
        kml_files += [os.path.join(root, f) for f in files]
    print('start creating database [cpu_count=%d].' % mp.cpu_count())
    args = [(kml_file, n_chars, dst_dir) for kml_file in kml_files]
    pool = mp.Pool()
    pool.map(make_db_entries, args)
    return

####

# make_db():
def make_db(dst_dir, ksj_files):
    t0 = time()

    n_chars = 7
    make_db01(ksj_files, n_chars, dst_dir)
    dir0 = os.path.dirname(os.path.realpath(__file__))
    shutil.copyfile(
        os.path.join(dir0, 'query_db.py'),
        os.path.join(dst_dir, 'query_db.py'))
    shutil.copyfile(
        os.path.join(dir0, 'geohash.py'),
        os.path.join(dst_dir, 'geohash.py'))

    print('Finished: %r' % (time() - t0))
    return

# main():
def main(args):
    make_db(args[0], args[1:])
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
