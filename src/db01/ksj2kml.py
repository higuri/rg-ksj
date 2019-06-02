#!/usr/bin/env python3
#
# ksj2kml.py
# - File Converter
# [Input]
# XML file [KSJ (Kokudo Suuchi Joho) - Administrative Boundaries]
# [Output]
# KML file (which defines polygons of administrative boundaries)

import sys
import xml.etree.ElementTree as ET
from .model import Point, Polygon, AdminArea

## XML Namespaces used in GML for KSJ (Kokudo Suuchi Jouho)
NS = {
    'gml': 'http://www.opengis.net/gml/3.2',
    'ksj': 'http://nlftp.mlit.go.jp/ksj/schemas/ksj-app',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'xlink': 'http://www.w3.org/1999/xlink'
}

# make_polygons():
def make_polygons(pos_list_text):
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

# make_kml_file():
def make_kml_file(admin_area, dstfile):
    f = open(dstfile, 'w')
    f.write('<?xml version="1.0" encoding="utf-8" standalone="no"?>\n')
    f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    f.write('<Document>\n')
    f.write('<name>%s</name>\n' % (admin_area.name))
    for (i, poly) in enumerate(admin_area.bounds):
        f.write('<Placemark id="%d">\n' % (i+1))
        f.write('<name>%d</name>\n' % (i+1))
        f.write('<Polygon>\n')
        f.write('<outerBoundaryIs>\n')
        f.write('<LinearRing>\n')
        f.write('<coordinates>\n')
        for p in poly.vertices:
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

# make_admin_areas():
def make_admin_areas(srcfile):
    tree = ET.parse(srcfile)
    root = tree.getroot()
    lat_lng_range = None
    # curve_id_to_polygon:
    curve_id_to_polygon = {}
    for curve in root.findall('gml:Curve', NS):
        id = curve.get('{%s}id' % NS['gml'])
        segments = curve.find('gml:segments', NS)
        segment = segments.find('gml:LineStringSegment', NS)
        posList = segment.find('gml:posList', NS)
        polygon = make_polygons(posList.text)
        curve_id_to_polygon[id] = polygon
        if lat_lng_range is None:
            lat_lng_range = polygon.get_range()
        else:
            lat_lng_range.union(polygon.get_range())
    # surface_id_2_curve_id:
    surface_id_2_curve_id = {}
    for surface in root.findall('gml:Surface', NS):
        id = surface.get('{%s}id' % NS['gml'])
        patches = surface.find('gml:patches', NS)
        patch = patches.find('gml:PolygonPatch', NS)
        exterior = patch.find('gml:exterior', NS)
        # TODO: interior
        ring = exterior.find('gml:Ring', NS)
        curveMember = ring.find('gml:curveMember', NS)
        curveRef = curveMember.get('{%s}href' % NS['xlink'])
        surface_id_2_curve_id[id] = curveRef.replace('#', '')
    # surface_id_to_polygon
    def surface_id_to_polygon(surfaceId):
        curveId = surface_id_2_curve_id[surfaceId]
        polygon = curve_id_to_polygon[curveId]
        return polygon
    # area_code_to_polygons / area_code_to_name
    area_code_to_polygons = {}
    area_code_to_name = {}
    for boundary in root.findall('ksj:AdministrativeBoundary', NS):
        bounds = boundary.find('ksj:bounds', NS)
        e0 = boundary.find('ksj:administrativeAreaCode', NS)
        e1 = boundary.find('ksj:prefectureName', NS)
        e2 = boundary.find('ksj:cityName', NS)
        if (e0 is None or e1 is None or e2 is None):
            continue
        if (e0.text is None or e1.text is None or e2.text is None):
            # area code of '所属未定地' is None.
            continue
        area_code = e0.text.strip()
        pref_name = e1.text.strip()
        city_name = e2.text.strip()
        if area_code not in area_code_to_polygons:
            area_code_to_polygons[area_code] = []
        if area_code not in area_code_to_name:
            area_code_to_name[area_code] = '%s,%s' % (pref_name, city_name)
        boundsRef = bounds.get('{%s}href' % NS['xlink'])
        polygon = surface_id_to_polygon(boundsRef.replace('#', ''))
        area_code_to_polygons[area_code].append(polygon)
    # admin_areas
    admin_areas = []
    for (area_code, polygons) in area_code_to_polygons.items():
        name = area_code_to_name[area_code]
        admin_area = AdminArea(area_code, name, polygons)
        admin_areas.append(admin_area)
    return (admin_areas, lat_lng_range)

# main()
def main(args):
    # TODO
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
