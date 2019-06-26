#!/usr/bin/env python3
# make_db.py
# - Make DB for reverse geocodeing from KSJ (Kokudo Suuchi Jouhou) files.
# [Input]
# - XML files of Kokudo Suuchi Jouhou - Administrative Boundaries
#   Data Source:
#   http://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-v2_3.html
# [Output]
# TODO:
# - fs
# - json
# - cdb
#      

from glob import glob
import json
import os
import shutil
import sys
from time import time
import multiprocessing as mp
import re
import sys
import xml.etree.ElementTree as ET
from .cdb import cdbmake
from .geohash import decode_to_range
from .geohash import get_longest_geohash, get_sub_geohashes
from shapely.geometry import Point, Polygon

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

# get_pref_code():
def get_pref_code(area_code):
    return area_code[:2]

# get_area_code():
def get_area_code(kml_file):
    return os.path.splitext(os.path.basename(kml_file))[0]

# make_polygon()
def make_polygon(lat_lng_range):
    ((minlat, maxlat), (minlng, maxlng)) = lat_lng_range
    return Polygon([
        (minlat, minlng),
        (minlat, maxlng),
        (maxlat, maxlng),
        (maxlat, minlng),
        (minlat, minlng)
    ])

# make_point()
def make_point(lat_lng_range):
    ((minlat, maxlat), (minlng, maxlng)) = lat_lng_range
    return Point((minlat + maxlat) / 2, (maxlat + maxlng) / 2)

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
        return (points, ((minlat, maxlat), (minlng, maxlng)))
    retval = []
    tree = ET.parse(kml_file)
    root = tree.getroot()
    kml_doc = root.find('kml:Document', KML_NS)
    for placemark in kml_doc.findall('kml:Placemark', KML_NS):
        for kml_polygon in placemark.findall('kml:Polygon', KML_NS):
            # outerBoundary (exterios)
            bounds = kml_polygon.find('kml:outerBoundaryIs', KML_NS)
            ring = bounds.find('kml:LinearRing', KML_NS)
            coords = ring.find('kml:coordinates', KML_NS)
            (outer_points, lat_lng_range) = parse_coords_lines(coords.text)
            # innerBoundary (interior)
            inner_points = []
            for bounds in kml_polygon.findall('kml:innerBoundaryIs', KML_NS):
                ring = bounds.find('kml:LinearRing', KML_NS)
                coords = ring.find('kml:coordinates', KML_NS)
                inner_points.append(parse_coords_lines(coords.text)[0])
            polygon = Polygon(outer_points, inner_points)
            retval.append((polygon, lat_lng_range))
    return retval

# find_nearest_polygon():
#   find the nearest polygon to geohash area
#   from polygons defined in kml_files.
def find_nearest_polygon(geohash, kml_files):
    assert 0 < len(kml_files)
    lat_lng_range = decode_to_range(geohash)
    polygon0 = make_polygon(lat_lng_range)
    min_distance = None
    min_kml_file = None
    for kml_file in kml_files:
        for (polygon1, _) in make_polygons(kml_file):
            d = polygon0.distance(polygon1)
            if min_distance is None or d < min_distance:
                min_distance = d
                min_kml_file = kml_file
    assert min_kml_file is not None
    return min_kml_file

# make_polygon_from_ext_ints():
def make_polygon_from_ext_ints(exterior_kml_file, interior_kml_files):
    polygons0 = make_polygons(exterior_kml_file)
    assert len(polygons0) == 1
    (polygon0, _) = polygons0[0]
    interior_points = []
    for interior_kml_file in interior_kml_files:
        polygons1 = make_polygons(interior_kml_file)
        assert len(polygons1) == 1
        (polygon1, _) = polygons1[0]
        interior_points.append(polygon1.exterior.coords)
    return Polygon(polygon0.exterior.coords, interior_points)

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
        # outerBoundary (exterior)
        f.write('<outerBoundaryIs>\n')
        f.write('<LinearRing>\n')
        f.write('<coordinates>\n')
        for (lat, lng) in polygon.exterior.coords:
            f.write(' %s,%s\n' % (lng, lat))
        f.write('</coordinates>\n')
        f.write('</LinearRing>\n')
        f.write('</outerBoundaryIs>\n')
        # innerBoundary (interior)
        for interior in polygon.interiors:
            f.write('<innerBoundaryIs>\n')
            f.write('<LinearRing>\n')
            f.write('<coordinates>\n')
            for (lat, lng) in interior.coords:
                f.write(' %s,%s\n' % (lng, lat))
            f.write('</coordinates>\n')
            f.write('</LinearRing>\n')
            f.write('</innerBoundaryIs>\n')
        f.write('</Polygon>\n')
        f.write('</Placemark>\n')
    f.write('</Document>\n')
    f.write('</kml>\n')
    f.close()
    return

# make_sfid2cvids():
def make_sfid2cvids(etree_root):
    # surface_id -> (exterior_curve_id, [interior_curve_id,..])
    sfid2cvids = {}
    for surface in etree_root.findall('gml:Surface', KSJ_NS):
        surface_id = surface.get('{%s}id' % KSJ_NS['gml'])
        patches = surface.find('gml:patches', KSJ_NS)
        patch = patches.find('gml:PolygonPatch', KSJ_NS)
        # Polygon:exterior
        exterior = patch.find('gml:exterior', KSJ_NS)
        ext_ring = exterior.find('gml:Ring', KSJ_NS)
        ext_curveMember = ext_ring.find('gml:curveMember', KSJ_NS)
        ext_curveRef = ext_curveMember.get('{%s}href' % KSJ_NS['xlink'])
        ext_curve_id = ext_curveRef.replace('#', '')
        # Polygon:interior
        interiors = patch.findall('gml:interior', KSJ_NS)
        int_curve_ids = []
        for interior in interiors:
            int_ring = interior.find('gml:Ring', KSJ_NS)
            int_curveMember = int_ring.find('gml:curveMember', KSJ_NS)
            int_curveRef = int_curveMember.get(
                '{%s}href' % KSJ_NS['xlink'])
            int_curve_id = int_curveRef.replace('#', '')
            int_curve_ids.append(int_curve_id)
        sfid2cvids[surface_id] = (ext_curve_id, int_curve_ids)
    return sfid2cvids

# make_areacode2sfids():
def make_areacode2sfids(ksj_root):
    areacode2sfids = {}
    areacode2areaname = {}
    for boundary in ksj_root.findall('ksj:AdministrativeBoundary', KSJ_NS):
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

# make_curve_files():
def make_curve_files(ksj_root, get_curve_fpath):
    # make_polygon():
    def make_polygon(pos_list_text):
        points = []
        for line in pos_list_text.splitlines():
             s = line.strip()
             if 0 < len(s):
                (lat, lng) = [float(v) for v in s.split(' ')]
                points.append((lat, lng))
        return Polygon(points)
    for curve in ksj_root.findall('gml:Curve', KSJ_NS):
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

# make_areacode2curvefiles():
def make_areacode2curvefiles(ksj_root, get_curve_fpath):
    sfid2cvids = make_sfid2cvids(ksj_root)
    (areacode2sfids, areacode2areaname) = make_areacode2sfids(ksj_root)
    # areacode2curvefiles
    # - key: area_code
    # - val: (interior_curve_id, [exterior_curve_id, ...]), ...
    areacode2curvefiles = {}
    for (area_code, surface_ids) in areacode2sfids.items():
        areacode2curvefiles[area_code] = []
        for surface_id in surface_ids:
            # surface_id -> curve_id (exterior_id, [interior_id,...])
            (ext_cvid, int_cvids) = sfid2cvids[surface_id]
            # curve_id -> curve file set (exterior, interiors)
            curve_file_set = (
                get_curve_fpath(ext_cvid),
                [get_curve_fpath(int_cvid) for int_cvid in int_cvids]
            )
            areacode2curvefiles[area_code].append(curve_file_set)
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
    # get_curve_fpath():
    CURVE_ID_PAT = re.compile(r'cv([0-9]+)_[0-9]+')
    def get_curve_fpath(curve_id):
        m = CURVE_ID_PAT.match(curve_id)
        assert m is not None
        i = int(m.group(1))
        # up to 1000 files per directory (for debuggability).
        dpath = os.path.join(tmp_dir, str(i // 1000))
        return os.path.join(dpath, curve_id + '.kml')
    # ksj_file -> {area_code: [curve_file(.kml)...]}
    #   write out ksj:Curve objects (boundary fragments) to KML files.
    ksj_root = ET.parse(ksj_file).getroot()
    # ksj_root -> curve files (.kml)
    make_curve_files(ksj_root, get_curve_fpath)
    # ksj_root -> {area_code: [(int_curve_file, ext_curve_files), ...]}
    areacode2curvefiles = make_areacode2curvefiles(
        ksj_root, get_curve_fpath)
    kml_files = []
    for (area_code, curve_files) in areacode2curvefiles.items():
        polygons = []
        # curve_file -> [polygon...]
        for (exterior_curve_file, interior_curve_files) in curve_files:
            polygon = make_polygon_from_ext_ints(
                exterior_curve_file, interior_curve_files)
            polygons.append(polygon)
        # kml/: [polygon...] -> .kml
        pref_dir = os.path.join(dst_dir, get_pref_code(area_code))
        if not os.path.isdir(pref_dir):
            os.makedirs(pref_dir)
        kml_file = os.path.join(pref_dir, area_code + '.kml')
        make_kml_file(polygons, area_code, kml_file)
        kml_files.append(kml_file)
        print('Finished: writing %s' % kml_file)
    shutil.rmtree(tmp_dir)
    return kml_files

# make_areacode_directories()
def make_areacode_directories(json_files, areacode_dir):
    # write_entry()
    def write_entry(geohash, area_code):
        fpath = os.path.join(
            areacode_dir, os.path.sep.join(geohash))
        # - No duplication of geohash (one geohash -> one area code).
        assert not os.path.isfile(fpath)
        # - The sub-geohashes of the geohash whose area code is
        #   already defined don't have their area code definitions.
        dirpath = os.path.dirname(fpath)
        assert not os.path.isdir(fpath)
        assert not os.path.isfile(dirpath)
        if not os.path.isdir(os.path.dirname(fpath)):
            os.makedirs(os.path.dirname(fpath))
        with open(fpath, 'w') as fp:
            fp.write(area_code)
        return
    #
    for json_file in json_files:
        with open(json_file, 'r') as fp:
            geohash2areacode = json.load(fp)
            for (geohash, area_code) in geohash2areacode.items():
                write_entry(geohash, area_code)
    return

# review_json_files():
def review_json_files(review_dir, dst_json):
    with open(dst_json, 'w') as fdst:
        fdst.write('{')
        isFirstItem = True
        for review_file in os.listdir(review_dir):
            geohash = os.path.basename(review_file)
            fpath = os.path.join(review_dir, review_file)
            with open(fpath, 'r') as fsrc:
                kml_files = [
                    line for line in fsrc.read().splitlines()
                    if line.strip() != ''
                ]
                area_code = None
                if len(kml_files) < 1:
                    continue
                elif len(kml_files) == 1:
                    area_code = get_area_code(kml_files[0])
                else:
                    kml_file = find_nearest_polygon(geohash, kml_files)
                    area_code = get_area_code(kml_file)
                assert(area_code is not None)
                if isFirstItem:
                    fdst.write('"%s": "%s"' % (geohash, area_code))
                    isFirstItem = False
                else:
                    fdst.write(',"%s": "%s"' % (geohash, area_code))
        fdst.write('}')
    return

# merge_json_files():
def merge_json_files(json_files, json_file):
    with open(json_file, 'w') as fdst:
        fdst.write('{')
        for (i, src) in enumerate(json_files):
            with open(src, 'r') as fsrc:
                # we treat this file as plain text file,
                # instead of parsing as json file (for efficiency).
                s = fsrc.read()
                assert s[0] == '{' and s[-1] == '}'
                fdst.write(s[1:-1])
                if i != len(json_files) - 1:
                    fdst.write(',')
        fdst.write('}')
    return

# make_cdb():
def make_cdb(json_files, cdb_file):
    cdb_writer = cdbmake(cdb_file)
    for (i, src) in enumerate(json_files):
        with open(src, 'r') as fsrc:
            for (k, v) in json.load(fsrc).items():
                cdb_writer.add(k.encode(), v.encode())
    cdb_writer.finish()
    return

# make_json():
def make_json(args): 
    (kml_file, n_kml_files, n_geohash, json_dir, review_dir) = args
    area_code = get_area_code(kml_file)
    # geohashes whose area code is $area_code.
    geohashes = []
    # geohashes that may contain more than two area codes,
    # one of them is $area_code.
    geohashes_to_be_reviewed = {}
    def add_to_review(geohash):
        if geohash in geohashes_to_be_reviewed:
            geohashes_to_be_reviewed[geohash].add(kml_file)
        else:
            geohashes_to_be_reviewed[geohash] = {kml_file}  # set
    #
    def doit(geohash, polygon):
        for (geohash1, range1) in get_sub_geohashes(geohash):
            polygon1 = make_polygon(range1)
            if polygon.intersects(polygon1):
                if polygon.contains(polygon1):
                    geohashes.append(geohash1)
                elif len(geohash1) < n_geohash:
                    doit(geohash1, polygon)
                else:
                    # TODO: this makes process slow...
                    add_to_review(geohash1)
            else:
                # polygon1 is outside of polygon.
                pass    # nop
        return
    #
    t0 = time()
    for (polygon, lat_lng_range) in make_polygons(kml_file):
        geohash = get_longest_geohash(lat_lng_range, n_geohash)
        if len(geohash) < n_geohash:
            doit(geohash, polygon)
        else:
            add_to_review(geohash)
    # write json files:
    pref_dir = os.path.join(json_dir, get_pref_code(area_code))
    if not os.path.isdir(pref_dir):
        os.makedirs(pref_dir)
    json_file = os.path.join(pref_dir, area_code + '.json')
    geohash2areacode = {geohash: area_code for geohash in geohashes}
    with open(json_file, 'w') as fp:
        json.dump(geohash2areacode, fp, indent=None)
    # write files to be reviewed:
    for (geohash1, kml_files1) in geohashes_to_be_reviewed.items():
        # write file: ${review_dir}/${geohash1}
        review_file = os.path.join(review_dir, geohash1)
        with open(review_file, 'a') as fp:
            for kml_file1 in kml_files1:
                fp.write(kml_file1 + '\n')
    i_files = len(glob(json_dir + '/**/*.json', recursive=True))
    print('Finished: [%d/%d] %s -> %s (%.2f sec)' % (
        i_files, n_kml_files, kml_file, json_file, time() - t0))
    return

####

# make_db():
def make_db(ksj_files, db_type, build_dir, dst_db_path, n_geohash=7):
    t0 = time()
    # ${build_dir}/kml
    kml_dir = os.path.join(build_dir, 'kml')
    kml_files = []
    for ksj_file in ksj_files:
        # parse
        print('reading: %s...' % ksj_file)
        kml_files += make_kml_files(ksj_file, kml_dir)
    # ${build_dir}/geohash
    print('start creating database.')
    print('- ksj_files: %s' % ','.join(ksj_files))
    print('- build_dir: %s' % build_dir)
    print('- db_type: %s' % db_type)
    print('- geohash_length: %d' % n_geohash)
    print('- cpu_count: %d' % mp.cpu_count())
    json_dir = os.path.join(build_dir, 'json')
    review_dir = os.path.join(build_dir, 'review')
    assert not os.path.isdir(json_dir)
    assert not os.path.isdir(review_dir)
    os.makedirs(json_dir)
    os.makedirs(review_dir)
    mp_args = [
        (kml_file, len(kml_files), n_geohash, json_dir, review_dir)
        for kml_file in kml_files
    ]
    pool = mp.Pool()
    pool.map(make_json, mp_args)
    review_json_files(review_dir, os.path.join(json_dir, 'reviewed.json'))
    json_files = glob(json_dir + '/**/*.json', recursive=True)
    if db_type == 'json':
        print('Merging json files...')
        merge_json_files(json_files, dst_db_path)
    elif db_type == 'cdb':
        print('Making a cdb file from json files...')
        make_cdb(json_files, dst_db_path)
    elif db_type == 'fs':
        print('Making a database in the form of file structure...')
        make_areacode_directories(json_files, dst_db_path)
    print('Finished: %.2f sec' % (time() - t0))
    return

# main():
def main(args):
    make_db(args[0], args[1:])
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
