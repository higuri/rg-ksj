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
        return '<Point lat=%f lng=%f>' % (self.lat, self.lng)
    # x:
    @property
    def x(self):
        return self.lng
    # y:
    @property
    def y(self):
        return self.lat
    # is_same_coordinate():
    def is_same_coordinate(self, other):
        return self.lat == other.lat and self.lng == other.lng

## Polygon
class Polygon:
    # Polygon()
    def __init__(self, vertices):
        self.vertices = vertices
        return

    # __repr__
    def __repr__(self):
        return '<Polygon vertices=%d>' % (len(self.vertices))

    # contains()
    def contains(self, p):
        # ray casting algorithm.
        nIntersects = 0
        for i in range(len(self.vertices) - 1):
            v0 = self.vertices[i]       # start point
            v1 = self.vertices[i+1]     # end point
            # upward edge: includes v0 and excludes v1.
            # downward edge: excludes v0 includes v1.
            if ((v0.y <= p.y and p.y < v1.y) or
                (p.y < v0.y and v1.y <= p.y)):
                # edge is on the right of p (without overwrapping)
                vt = (p.y - v0.y) / (v1.y - v0.y)
                if p.x < (v0.x + (vt * (v1.x - v0.x))):
                    nIntersects += 1
        return not (nIntersects % 2 == 0)
