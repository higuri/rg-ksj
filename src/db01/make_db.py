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

import sys
import os
import shutil
import re
import sys
import xml.etree.ElementTree as ET
from .model import Point, Polygon

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

# make_polygons(): kml_file -> [polygon]
def make_polygons(kml_file):
    def parse_coords_lines(lines):
        points = []
        for line in lines.splitlines():
            s = line.strip()
            if 0 < len(s):
                (lng, lat) = s.split(',')
                point = Point(lat, lng)
                points.append(point)
        return Polygon(points)
    polygons = []
    tree = ET.parse(kml_file)
    root = tree.getroot()
    kml_doc = root.find('kml:Document', KML_NS)
    for placemark in kml_doc.findall('kml:Placemark', KML_NS):
        for polygon in placemark.findall('kml:Polygon', KML_NS):
            bounds = polygon.find('kml:outerBoundaryIs', KML_NS)
            ring = bounds.find('kml:LinearRing', KML_NS)
            coords = ring.find('kml:coordinates', KML_NS)
            polygon = parse_coords_lines(coords.text)
            polygons.append(polygon)
    return polygons

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
        for p in polygon.vertices:
            f.write(' %s,%s\n' % (p.lng, p.lat))
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
                (lat, lng) = s.split(' ')
                point = Point(lat, lng)
                points.append(point)
        # 閉じられていること。
        assert(points[0].is_same_coordinate(points[-1]))
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
def make_kml_files(ksj_file, dst_dir):
    # kml_dir: 'kml/' - contains KML files which define
    #          polygons of administrative boundaries.
    kml_dir = os.path.join(dst_dir, 'kml')
    # index_dir: 'kml-index/' - contains index files for 'kml/',
    #            for improving search efficiency.
    index_dir = os.path.join(dst_dir, 'kml-index')
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
    # lat_lng_range: defines max/min lat and lng in 'kml/'.
    lat_lng_range = None
    ##
    # ksj_file -> {area_code: [curve_file(.kml)...]}
    #   write out ksj:Curve objects (boundary fragments) to KML files.
    areacode2curvefiles = make_curve_files(ksj_file, tmp_dir)
    for (area_code, curve_files) in areacode2curvefiles.items():
        polygons = []
        # curve_file -> [polygon...]
        for curve_file in curve_files:
            polygons1 = make_polygons(curve_file)
            for polygon in polygons1:
                r = polygon.get_range()
                if lat_lng_range is None:
                    lat_lng_range = r
                else:
                    lat_lng_range.union(r)
            polygons += polygons1
        # kml/: [polygon...] -> .kml
        pref_code = area_code[:2]
        pref_dir = os.path.join(kml_dir, pref_code)
        if not os.path.isdir(pref_dir):
            os.makedirs(pref_dir)
        kml_path = os.path.join(pref_dir, area_code + '.kml')
        print('writing: %s...' % kml_path)
        make_kml_file(polygons, area_code, kml_path)
        # kml-index/:
        for index_path in get_index_file_paths(polygons, index_dir):
            print('writing: %s...' % index_path)
            dirname = os.path.dirname(index_path)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            if os.path.isfile(index_path):
                f = open(index_path, 'a')
                f.write(',' + area_code)
                f.close()
            else:
                f = open(index_path, 'w')
                f.write(area_code)
                f.close()
    shutil.rmtree(tmp_dir)
    return lat_lng_range

# make_db():
def make_db(ksj_files, dst_dir='.'):
    lat_lng_range = None
    for ksj_file in ksj_files:
        # parse
        print('reading: %s...' % ksj_file)
        r = make_kml_files(ksj_file, dst_dir)
        if lat_lng_range is None:
            lat_lng_range = r
        else:
            lat_lng_range.union(r)
    return lat_lng_range

# main()
def main(args):
    make_db(args)
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
