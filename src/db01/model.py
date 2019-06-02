#!/usr/bin/env python3
#
# model.py
# - Defines data types for rg-ksj.
#

## Point
class Point:
    # Point():
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng
        return
    # __repr__
    def __repr__(self):
        return '<Point lat=%s lng=%s>' % (self.lat, self.lng)
    # x:
    @property
    def x(self):
        # TODO: precision
        return float(self.lng)
    # y:
    @property
    def y(self):
        return float(self.lat)
    # is_same_coordinate():
    def is_same_coordinate(self, other):
        return self.lat == other.lat and self.lng == other.lng

## Rect
class Rect:
    # Rect()
    def __init__(self, lower_left, upper_right):
        self.lower_left = lower_left
        self.upper_right = upper_right
        return
    # __repr__
    def __repr__(self):
        return '<Rect lower_left=%r upper_right=%r>' % (
            self.lower_left, self.upper_right)
    @property
    def minx(self):
        return self.lower_left.x
    @property
    def miny(self):
        return self.lower_left.y
    @property
    def maxx(self):
        return self.upper_right.x
    @property
    def maxy(self):
        return self.upper_right.y

    # union()
    def union(self, other):
        minx = other.minx if other.minx < self.minx else self.minx
        miny = other.miny if other.miny < self.miny else self.miny
        maxx = other.maxx if self.maxx < other.maxx else self.maxx
        maxy = other.maxy if self.maxy < other.maxy else self.maxy
        self.lower_left = Point(str(miny), str(minx))
        self.upper_right = Point(str(maxy), str(maxx))
        return

## Polygon
class Polygon:
    # Polygon()
    def __init__(self, vertices):
        self.vertices = vertices
        return

    # __repr__
    def __repr__(self):
        return '<Polygon vertices=%d>' % (len(self.vertices))

    # get_range():
    def get_range(self):
        v = self.vertices
        assert(0 < len(v))
        minx = maxx = v[0].x
        miny = maxy = v[0].y
        for p in v[1:]:
            if p.x < minx: minx = p.x
            if p.y < miny: miny = p.y
            if maxx < p.x: maxx = p.x
            if maxy < p.y: maxy = p.y
        return Rect(
            Point(str(miny), str(minx)),
            Point(str(maxy), str(maxx)))

    # contains()
    def contains(self, p):
        # ray casting algorithm.
        nIntersects = 0
        for i in range(len(self.vertices) - 1):
            v0 = self.vertices[i]       # 始点
            v1 = self.vertices[i+1]     # 終点
            # 上向きの辺: 開始点を含み終点を含まない。
            # 下向きの辺: 開始点を含まず終点を含む。
            if ((v0.y <= p.y and p.y < v1.y) or
                (p.y < v0.y and v1.y <= p.y)):
                # 辺はpよりも右側にある。ただし、重ならない。
                # 辺がpと同じ高さになる位置における
                # xの値とp.xの値を比較する。
                vt = (p.y - v0.y) / (v1.y - v0.y)
                if p.x < (v0.x + (vt * (v1.x - v0.x))):
                    nIntersects += 1
        return not (nIntersects % 2 == 0)

## AdminArea
class AdminArea:
    # AdminArea()
    def __init__(self, id, name, bounds):
        self.id = id    # AreaCode
        self.name = name
        self.bounds = bounds
        return

    # pref_code:
    @property
    def pref_code(self):
        return self.id[:2]

