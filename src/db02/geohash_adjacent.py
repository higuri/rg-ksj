#!/usr/bin/env python3
# geohash_adjacent.py
# - get geohashes adjacent to specified geohash.
#

# ----------------
# | NW | NN | NE |
# |--------------|
# | WW | AA | EE |
# |--------------|
# | SW | SS | SE |
# ----------------
NW = 0    # NorthWest
NN = 1    # North
NE = 2    # NorthEast
WW = 3    # West
EE = 4    # East
SW = 5    # SouthWest
SS = 6    # South
SE = 7    # SouthEast
AA = 10   # Here (Self)

# n = (1, 3, 5, ...) [odd]
#   n : length of geohash
#   ---------------------------------
#   | b | c | f | g | u | v | y | z |
#   ---------------------------------
#   | 8 | 9 | d | e | s | t | w | x |
#   ---------------------------------
#   | 2 | 3 | 6 | 7 | k | m | q | r |
#   ---------------------------------
#   | 0 | 1 | 4 | 5 | h | j | n | p |
#   ---------------------------------

adjacent_chars_odd = {
    '0': [
        (WW, 'r'), (AA, '2'), (AA, '3'),
        (WW, 'p'),            (AA, '1'),
        (SW, 'z'), (SS, 'b'), (SS, 'c')
    ],
    '1': [
        (AA, '2'), (AA, '3'), (AA, '6'),
        (AA, '0'),            (AA, '4'),
        (SS, 'b'), (SS, 'c'), (SS, 'f')
    ],
    '2': [
        (WW, 'x'), (AA, '8'), (AA, '9'),
        (WW, 'r'),            (AA, '3'),
        (WW, 'p'), (AA, '0'), (AA, '1')
    ],
    '3': [
        (AA, '8'), (AA, '9'), (AA, 'd'),
        (AA, '2'),            (AA, '6'),
        (AA, '0'), (AA, '1'), (AA, '4')
    ],
    '4': [
        (AA, '3'), (AA, '6'), (AA, '7'),
        (AA, '1'),            (AA, '5'),
        (SS, 'c'), (SS, 'f'), (SS, 'g')
    ],
    '5': [
        (AA, '6'), (AA, '7'), (AA, 'k'),
        (AA, '4'),            (AA, 'h'),
        (SS, 'f'), (SS, 'g'), (SS, 'u')
    ],
    '6': [
        (AA, '9'), (AA, 'd'), (AA, 'e'),
        (AA, '3'),            (AA, '7'),
        (AA, '1'), (AA, '4'), (AA, '5')
    ],
    '7': [
        (AA, 'd'), (AA, 'e'), (AA, 's'),
        (AA, '6'),            (AA, 'k'),
        (AA, '4'), (AA, '5'), (AA, 'h')
    ],
    '8': [
        (WW, 'z'), (AA, 'b'), (AA, 'c'),
        (WW, 'x'),            (AA, '9'),
        (WW, 'r'), (AA, '2'), (AA, '3')
    ],
    '9': [
        (AA, 'b'), (AA, 'c'), (AA, 'f'),
        (AA, '8'),            (AA, 'd'),
        (AA, '2'), (AA, '3'), (AA, '6')
    ],
    'b': [
        (NW, 'p'), (NN, '0'), (NN, '1'),
        (WW, 'z'),            (AA, 'c'),
        (WW, 'x'), (AA, '8'), (AA, '9')
    ],
    'c': [
        (NN, '0'), (NN, '1'), (NN, '4'),
        (AA, 'b'),            (AA, 'f'),
        (AA, '8'), (AA, '9'), (AA, 'd')
    ],
    'd': [
        (AA, 'c'), (AA, 'f'), (AA, 'g'),
        (AA, '9'),            (AA, 'e'),
        (AA, '3'), (AA, '6'), (AA, '7')
    ],
    'e': [
        (AA, 'f'), (AA, 'g'), (AA, 'u'),
        (AA, 'd'),            (AA, 's'),
        (AA, '6'), (AA, '7'), (AA, 'k')
    ],
    'f': [
        (NN, '1'), (NN, '4'), (NN, '5'),
        (AA, 'c'),            (AA, 'g'),
        (AA, '9'), (AA, 'd'), (AA, 'e')
    ],
    'g': [
        (NN, '4'), (NN, '5'), (NN, 'h'),
        (AA, 'f'),            (AA, 'u'),
        (AA, 'd'), (AA, 'e'), (AA, 's')
    ],
    'h': [
        (AA, '7'), (AA, 'k'), (AA, 'm'),
        (AA, '5'),            (AA, 'j'),
        (SS, 'g'), (SS, 'u'), (SS, 'v')
    ],
    'j': [
        (AA, 'k'), (AA, 'm'), (AA, 'q'),
        (AA, 'h'),            (AA, 'n'),
        (SS, 'u'), (SS, 'v'), (SS, 'y')
    ],
    'k': [
        (AA, 'e'), (AA, 's'), (AA, 't'),
        (AA, '7'),            (AA, 'm'),
        (AA, '5'), (AA, 'h'), (AA, 'j')
    ],
    'm': [
        (AA, 's'), (AA, 't'), (AA, 'w'),
        (AA, 'k'),            (AA, 'q'),
        (AA, 'h'), (AA, 'j'), (AA, 'n')
    ],
    'n': [
        (AA, 'm'), (AA, 'q'), (AA, 'r'),
        (AA, 'j'),            (AA, 'p'),
        (SS, 'v'), (SS, 'y'), (SS, 'z')
    ],
    'p': [
        (AA, 'q'), (AA, 'r'), (EE, '2'),
        (AA, 'n'),            (EE, '0'),
        (AA, 'y'), (AA, 'z'), (EE, 'b')
    ],
    'q': [
        (AA, 't'), (AA, 'w'), (AA, 'x'),
        (AA, 'm'),            (AA, 'r'),
        (AA, 'j'), (AA, 'n'), (AA, 'p')
    ],
    'r': [
        (AA, 'w'), (AA, 'x'), (EE, '8'),
        (AA, 'q'),            (EE, '2'),
        (AA, 'n'), (AA, 'p'), (EE, '0')
    ],
    's': [
        (AA, 'g'), (AA, 'u'), (AA, 'v'),
        (AA, 'e'),            (AA, 't'),
        (AA, '7'), (AA, 'k'), (AA, 'm')
    ],
    't': [
        (AA, 'u'), (AA, 'v'), (AA, 'y'),
        (AA, 's'),            (AA, 'w'),
        (AA, 'k'), (AA, 'm'), (AA, 'q')
    ],
    'u': [
        (NN, '5'), (NN, 'h'), (NN, 'j'),
        (AA, 'g'),            (AA, 'v'),
        (AA, 'e'), (AA, 's'), (AA, 't')
    ],
    'v': [
        (NN, 'h'), (NN, 'j'), (NN, 'n'),
        (AA, 'u'),            (AA, 'y'),
        (AA, 's'), (AA, 't'), (AA, 'w')
    ],
    'w': [
        (AA, 'v'), (AA, 'y'), (AA, 'z'),
        (AA, 't'),            (AA, 'x'),
        (AA, 'm'), (AA, 'q'), (AA, 'r')
    ],
    'x': [
        (AA, 'y'), (AA, 'z'), (EE, 'b'),
        (AA, 'w'),            (EE, '8'),
        (AA, 'q'), (AA, 'r'), (EE, '2')
    ],
    'y': [
        (NN, 'j'), (NN, 'n'), (NN, 'p'),
        (AA, 'v'),            (AA, 'z'),
        (AA, 't'), (AA, 'w'), (AA, 'x')
    ],
    'z': [
        (NN, 'n'), (NN, 'p'), (NE, '0'),
        (AA, 'y'),            (EE, 'b'),
        (AA, 'w'), (AA, 'x'), (EE, '8')
    ]
}
assert(len(adjacent_chars_odd.keys()) == 32)


# n = (2, 4, 6, ...) [even]
#   n : length of geohash
#
#   -----------------
#   | p | r | x | z |
#   -----------------
#   | n | q | w | y |
#   -----------------
#   | j | m | t | v |
#   -----------------
#   | h | k | s | u |
#   -----------------
#   | 5 | 7 | e | g |
#   -----------------
#   | 4 | 6 | d | f |
#   -----------------
#   | 1 | 3 | 9 | c |
#   -----------------
#   | 0 | 2 | 8 | b |
#   -----------------
#

adjacent_chars_even = {
    '0': [
        (WW, 'c'), (AA, '1'), (AA, '3'),
        (WW, 'b'),            (AA, '2'),
        (SW, 'z'), (SS, 'p'), (SS, 'r')
    ],
    '1': [
        (WW, 'f'), (AA, '4'), (AA, '6'),
        (WW, 'c'),            (AA, '3'),
        (WW, 'b'), (AA, '0'), (AA, '2')
    ],
    '2': [
        (AA, '1'), (AA, '3'), (AA, '9'),
        (AA, '0'),            (AA, '8'),
        (SS, 'p'), (SS, 'r'), (SS, 'x')
    ],
    '3': [
        (AA, '4'), (AA, '6'), (AA, 'd'),
        (AA, '1'),            (AA, '9'),
        (AA, '0'), (AA, '2'), (AA, '8')
    ],
    '4': [
        (WW, 'g'), (AA, '5'), (AA, '7'),
        (WW, 'f'),            (AA, '6'),
        (WW, 'c'), (AA, '1'), (AA, '3')
    ],
    '5': [
        (WW, 'u'), (AA, 'h'), (AA, 'k'),
        (WW, 'g'),            (AA, '7'),
        (WW, 'f'), (AA, '4'), (AA, '6')
    ],
    '6': [
        (AA, '5'), (AA, '7'), (AA, 'e'),
        (AA, '4'),            (AA, 'd'),
        (AA, '1'), (AA, '3'), (AA, '9')
    ],
    '7': [
        (AA, 'h'), (AA, 'k'), (AA, 's'),
        (AA, '5'),            (AA, 'e'),
        (AA, '4'), (AA, '6'), (AA, 'd')
    ],
    '8': [
        (AA, '3'), (AA, '9'), (AA, 'c'),
        (AA, '2'),            (AA, 'b'),
        (SS, 'r'), (SS, 'x'), (SS, 'z')
    ],
    '9': [
        (AA, '6'), (AA, 'd'), (AA, 'f'),
        (AA, '3'),            (AA, 'c'),
        (AA, '2'), (AA, '8'), (AA, 'b')
    ],
    'b': [
        (AA, '9'), (AA, 'c'), (EE, '1'),
        (AA, '8'),            (EE, '0'),
        (SS, 'x'), (SS, 'z'), (SE, 'p')
    ],
    'c': [
        (AA, 'd'), (AA, 'f'), (EE, '4'),
        (AA, '9'),            (EE, '1'),
        (AA, '8'), (AA, 'b'), (EE, '0')
    ],
    'd': [
        (AA, '7'), (AA, 'e'), (AA, 'g'),
        (AA, '6'),            (AA, 'f'),
        (AA, '3'), (AA, '9'), (AA, 'c')
    ],
    'e': [
        (AA, 'k'), (AA, 's'), (AA, 'u'),
        (AA, '7'),            (AA, 'g'),
        (AA, '6'), (AA, 'p'), (AA, 'f')
    ],
    'f': [
        (AA, 'e'), (AA, 'g'), (EE, '5'),
        (AA, 'd'),            (EE, '4'),
        (AA, '9'), (AA, 'c'), (EE, '1')
    ],
    'g': [
        (AA, 's'), (AA, 'u'), (EE, 'h'),
        (AA, 'e'),            (EE, '5'),
        (AA, 'd'), (AA, 'f'), (EE, '4')
    ],
    'h': [
        (WW, 'v'), (AA, 'j'), (AA, 'm'),
        (WW, 'u'),            (AA, 'k'),
        (WW, 'g'), (AA, '5'), (AA, '7')
    ],
    'j': [
        (WW, 'y'), (AA, 'n'), (AA, 'q'),
        (WW, 'v'),            (AA, 'm'),
        (WW, 'u'), (AA, 'h'), (AA, 'k')
    ],
    'k': [
        (AA, 'j'), (AA, 'm'), (AA, 't'),
        (AA, 'h'),            (AA, 's'),
        (AA, '5'), (AA, '7'), (AA, 'e')
    ],
    'm': [
        (AA, 'n'), (AA, 'q'), (AA, 'w'),
        (AA, 'j'),            (AA, 't'),
        (AA, 'h'), (AA, 'k'), (AA, 's')
    ],
    'n': [
        (WW, 'z'), (AA, 'p'), (AA, 'r'),
        (WW, 'y'),            (AA, 'q'),
        (WW, 'v'), (AA, 'j'), (AA, 'm')
    ],
    'p': [
        (NW, 'b'), (NN, '0'), (NN, '2'),
        (WW, 'z'),            (AA, 'r'),
        (WW, 'y'), (AA, 'n'), (AA, 'q')
    ],
    'q': [
        (AA, 'p'), (AA, 'r'), (AA, 'x'),
        (AA, 'n'),            (AA, 'w'),
        (AA, 'j'), (AA, 'm'), (AA, 't')
    ],
    'r': [
        (NN, '0'), (NN, '2'), (NN, '8'),
        (AA, 'p'),            (AA, 'x'),
        (AA, 'n'), (AA, 'q'), (AA, 'w')
    ],
    's': [
        (AA, 'm'), (AA, 't'), (AA, 'v'),
        (AA, 'k'),            (AA, 'u'),
        (AA, '7'), (AA, 'e'), (AA, 'g')
    ],
    't': [
        (AA, 'q'), (AA, 'w'), (AA, 'y'),
        (AA, 'm'),            (AA, 'v'),
        (AA, 'k'), (AA, 's'), (AA, 'u')
    ],
    'u': [
        (AA, 't'), (AA, 'v'), (EE, 'j'),
        (AA, 's'),            (EE, 'h'),
        (AA, 'e'), (AA, 'g'), (EE, '5')
    ],
    'v': [
        (AA, 'w'), (AA, 'y'), (EE, 'n'),
        (AA, 't'),            (EE, 'j'),
        (AA, 's'), (AA, 'u'), (EE, 'h')
    ],
    'w': [
        (AA, 'r'), (AA, 'x'), (AA, 'z'),
        (AA, 'q'),            (AA, 'y'),
        (AA, 'm'), (AA, 't'), (AA, 'v')
    ],
    'x': [
        (NN, '2'), (NN, '8'), (NN, 'b'),
        (AA, 'r'),            (AA, 'z'),
        (AA, 'q'), (AA, 'w'), (AA, 'y')
    ],
    'y': [
        (AA, 'x'), (AA, 'z'), (EE, 'p'),
        (AA, 'w'),            (EE, 'n'),
        (AA, 't'), (AA, 'v'), (EE, 'j')
    ],
    'z': [
        (NN, '8'), (NN, 'b'), (NE, '0'),
        (AA, 'x'),            (EE, 'p'),
        (AA, 'w'), (AA, 'y'), (EE, 'n')
    ]
}
assert(len(adjacent_chars_even.keys()) == 32)

# get_adjacent()
def get_adjacent(geohash, direction):
    assert(0 < len(geohash))
    m = adjacent_chars_even if len(geohash) % 2 == 0 else adjacent_chars_odd
    base = geohash[:-1]
    c0 = geohash[-1]
    (d1, c1) = m[c0][direction]
    if d1 == AA:
        return base + c1
    elif 0 < len(base):
        return get_adjacent(base, d1) + c1
    else:
        raise ValueError

# get_adjacent_north_west()
def get_adjacent_north_westNW(geohash):
    return get_adjacent(geohash, NW)
# get_adjacent_north()
def get_adjacent_north(geohash):
    return get_adjacent(geohash, NN)
# get_adjacent_north_east()
def get_adjacent_north_east(geohash):
    return get_adjacent(geohash, NE)
# get_adjacent_west()
def get_adjacent_west(geohash):
    return get_adjacent(geohash, WW)
# get_adjacent_east()
def get_adjacent_east(geohash):
    return get_adjacent(geohash, EE)
# get_adjacent_south_west()
def get_adjacent_south_west(geohash):
    return get_adjacent(geohash, SW)
# get_adjacent_south()
def get_adjacent_south(geohash):
    return get_adjacent(geohash, SS)
# get_adjacent_south_east()
def get_adjacent_south_east(geohash):
    return get_adjacent(geohash, SE)

if __name__ == "__main__":
    from geohash import decode
    # adjacent north + east...
    h0 = 'nxzrvrt'
    for _ in range(100):
        h1 = h0
        for _ in range(100):
            h2 = get_adjacent_east(h1)
            (lat1, lng1) = decode(h1)
            (lat2, lng2) = decode(h2)
            assert(lat1 == lat2)
            assert(lng1[1] == lng2[0])
            h1 = h2
        h1 = get_adjacent_north(h0)
        (lat0, lng0) = decode(h0)
        (lat1, lng1) = decode(h1)
        assert(lat0[1] == lat1[0])
        assert(lng0 == lng1)
        h0 = h1
    # adjacent sourth + west...
    h0 = 'nxzrvrt'
    for _ in range(100):
        h1 = h0
        for _ in range(100):
            h2 = get_adjacent_west(h1)
            (lat1, lng1) = decode(h1)
            (lat2, lng2) = decode(h2)
            assert(lat1 == lat2)
            assert(lng1[0] == lng2[1])
            h1 = h2
        h1 = get_adjacent_south(h0)
        (lat0, lng0) = decode(h0)
        (lat1, lng1) = decode(h1)
        assert(lat0[0] == lat1[1])
        assert(lng0 == lng1)
        h0 = h1
    print('Test OK.')
