#!/usr/bin/env python3
# query_db.py

import os
import sys
import xml.etree.ElementTree as ET
from .model import Point, Polygon

## XML Namespaces used in KML.
NS = {
    'kml': 'http://www.opengis.net/kml/2.2'
}

# make_polygons():
def make_polygons(kml_file):
    def parse_coords_lines(lines):
        points = []
        for line in lines.splitlines():
            s = line.strip()
            if 0 < len(s):
                (lng, lat) = s.split(',')
                point = Point(lat, lng)
                points.append(point)
        # 閉じられていること。
        assert(points[0].is_same_coordinate(points[-1]))
        return Polygon(points)
    polygons = []
    tree = ET.parse(kml_file)
    root = tree.getroot()
    kml_doc = root.find('kml:Document', NS)
    for placemark in kml_doc.findall('kml:Placemark', NS):
        for polygon in placemark.findall('kml:Polygon', NS):
            bounds = polygon.find('kml:outerBoundaryIs', NS)
            ring = bounds.find('kml:LinearRing', NS)
            coords = ring.find('kml:coordinates', NS)
            polygon = parse_coords_lines(coords.text)
            polygons.append(polygon)
    return polygons

# get_index_file_path():
def get_index_file_path(p, db_dir):
    def fmt(v):
        v1 = int(v * 10)
        return (str(v1 // 10), str(v1 % 10))
    (x0, x1) = fmt(p.x)
    (y0, y1) = fmt(p.y)
    return os.path.join(db_dir, 'kml-index', y0, y1, x0, x1) + '.txt'

# get_kml_file_paths():
def get_kml_file_paths(p, db_dir):
    fpath = get_index_file_path(p, db_dir)
    if not os.path.isfile(fpath):
        return []
    kml_files = []
    f = open(fpath, 'r')
    line = f.readline()
    for area_code in line.split(','):
        pref_code = area_code[:2]
        fpath = os.path.join(
            db_dir, 'kml', pref_code, area_code) + '.kml'
        kml_files.append(fpath)
    f.close()
    return kml_files

# get_area_name():
def get_area_name(kml_file):
    tree = ET.parse(kml_file)
    root = tree.getroot()
    kml_doc = root.find('kml:Document', NS)
    name = kml_doc.find('kml:name', NS)
    return name.text

# get_area_code():
def get_area_code(kml_file):
    return os.path.splitext(os.path.basename(kml_file))[0]

# get_area():
def get_area(lat, lng, db_dir):
    p = Point(str(lat), str(lng))
    for kml_file in get_kml_file_paths(p, db_dir):
        if not os.path.isfile(kml_file):
            continue
        #print('reading: %s...' % (kml_file))
        polygons = make_polygons(kml_file)
        for polygon in polygons:
            if polygon.contains(p):
                #return get_area_name(kml_file)
                return get_area_code(kml_file)
    return None

# main():
def main(basedir, args):
    (lat, lng) = args[:2]
    print(get_area(lat, lng, basedir))
    return

if __name__ == "__main__":
    main(os.path.dirname(sys.argv[0]), sys.argv[1:])
