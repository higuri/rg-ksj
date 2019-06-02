#!/usr/bin/env python3
# query_db01.py

import collections
import os
from .geohash import decode
from ..db01.model import Point
from ..db01.query_db import get_kml_file_paths, make_polygons
from ..db01.query_db import get_area_code, get_area_name

## PartialPolygon
class PartialPolygon:
    # PartialPolygon()
    def __init__(self, area_code, vertices, edges):
        self.area_code = area_code
        self.vertices = vertices
        self.edges = edges
        return

    # __repr__
    def __repr__(self):
        return '<PolygonPartial area_code=%s edges=%d>' % (
            self.area_code, len(self.edges))

    # from_polygon():
    @classmethod
    def from_polygon(klass, area_code, polygon, lat_range):
        y = (lat_range[0] + lat_range[1]) / 2
        (lat0, lat1) = lat_range
        vertices = []
        edges = []
        for i in range(len(polygon.vertices)):
            v0 = polygon.vertices[i]
            # vertices
            if lat0 <= v0.y and v0.y <= lat1:
                vertices.append(v0)
            # edges
            if i < len(polygon.vertices) - 1:
                v1 = polygon.vertices[i+1]
                if ((v0.y <= y and y < v1.y) or
                    (y < v0.y and v1.y <= y)):
                    edges.append((v0, v1))
        if 0 < len(vertices) or 0 < len(edges):
            return PartialPolygon(area_code, vertices, edges)
        else:
            return None

    # contains():
    def contains(self, point):
        p = point
        nIntersects = 0
        for (v0, v1) in self.edges:
            vt = (p.y - v0.y) / (v1.y - v0.y)
            if p.x < (v0.x + (vt * (v1.x - v0.x))):
                nIntersects += 1
        return not (nIntersects % 2 == 0)

    # one_more_vertices_in():
    def one_more_vertices_in(self, lng_range):
        (lng0, lng1) = lng_range
        for v in self.vertices:
            if lng0 <= v.x and v.x <= lng1:
                return True
        return False


## PolygonCollection
class PolygonCollection:
    # PolygonCollection():
    def __init__(self, max_size = 30):
        # [(kml_file, [Polygon...])...]
        self._polygons = collections.deque([], max_size)
        # [((kml_file, lat), [PartialPolygon...])...]
        self._partial_polygons = collections.deque([], max_size)
        return

    # get_polygons_from_cache()
    def get_polygons_from_cache(self, kml_file):
        n = len(self._polygons)
        for i in range(n):
            # search end to top.
            j = (n - 1) - i
            (key, polygons) = self._polygons[j]
            if key == kml_file:
                return polygons
        return None

    # get_partial_polygons_from_cache()
    def get_partial_polygons_from_cache(self, kml_file, lat_range):
        n = len(self._partial_polygons)
        for i in range(n):
            # search end to top.
            j = (n - 1) - i
            (key, polygons) = self._partial_polygons[j]
            if key == (kml_file, lat_range):
                return polygons
        return None

    # make_polygons()
    def make_polygons(self, kml_file, lat_range):
        # kml_file -> Polygon
        polygons0 = self.get_polygons_from_cache(kml_file)
        if polygons0 is None:
            polygons0 = make_polygons(kml_file)
            self._polygons.append((kml_file, polygons0))
        # Polygon -> PartialPolygon
        area_code = get_area_code(kml_file)
        partial_polygons = []
        for polygon0 in polygons0:
            polygon1 = PartialPolygon.from_polygon(
                area_code, polygon0, lat_range)
            if polygon1 is not None:
                partial_polygons.append(polygon1)
        # append to cache.
        self._partial_polygons.append(
            ((kml_file, lat_range), partial_polygons))
        return partial_polygons

    # get_polygons():
    # TODO: cleanup (db_dir)
    def get_polygons(self, point, lat_range, db_dir):
        polygons = []
        for kml_file in get_kml_file_paths(point, db_dir):
            if not os.path.isfile(kml_file):
                continue
            # has cached polygons?
            polygons1 = self.get_partial_polygons_from_cache(
                kml_file, lat_range)
            if polygons1 is not None:
                polygons += polygons1
                continue
            # make polygons.
            polygons1 = self.make_polygons(kml_file, lat_range)
            polygons += polygons1
        return polygons

# get_area_by_point():
def get_area_by_point(point, polygons):
    for polygon in polygons:
        if polygon.contains(point):
            return polygon.area_code
    return None

# get_area_by_range():
def get_area_by_range(lng_range, polygons):
    for polygon in polygons:
        if polygon.one_more_vertices_in(lng_range):
            # first touch -> return
            return polygon.area_code
    return None

# get_area_by_geohash():
polygon_collection = PolygonCollection()    # TODO cleanup
def get_area_by_geohash(geohash, db_dir):
    (lat_range, lng_range) = decode(geohash)
    point = Point(
        str((lat_range[0] + lat_range[1]) / 2),
        str((lng_range[0] + lng_range[1]) / 2))
    polygons =  polygon_collection.get_polygons(point, lat_range, db_dir)
    area = get_area_by_point(point, polygons)
    if area is not None:
        return area
    return get_area_by_range(lng_range, polygons)

