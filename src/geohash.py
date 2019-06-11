#!/usr/bin/env python3
# geohash.py
# - encode (lat,lng) to geohash.
# - decode geohash to (lat_range,lng_range).
# Geohash:
# https://en.wikipedia.org/wiki/Geohash

# mid()
def mid(seq):
    assert(len(seq) == 2)
    return (seq[0] + seq[1]) / 2.0
# lower_half()
def lower_half(seq):
    assert(len(seq) == 2)
    return (seq[0], mid(seq))
# upper_half()
def upper_half(seq):
    assert(len(seq) == 2)
    return (mid(seq), seq[1])
# is_contained()
def is_contained(lat_lng_range0, lat_lng_range1):
    ((minlat0, maxlat0), (minlng0, maxlng0)) = lat_lng_range0
    ((minlat1, maxlat1), (minlng1, maxlng1)) = lat_lng_range1
    return (
        minlat1 <= minlat0 and maxlat0 <= maxlat1 and
        minlng1 <= minlng0 and maxlng0 <= maxlng1
    )

BASE32 = '0123456789bcdefghjkmnpqrstuvwxyz'
BASE32_TO_DECIMAL = dict((BASE32[i], i) for i in range(len(BASE32)))
def bits2char(bits):
    return BASE32[bits]
def char2bits(char):
    return BASE32_TO_DECIMAL[char]

# get_char()
def get_char(i_chars, lat_lng, lat_lng_range):
    (lat, lng) = lat_lng
    (lat_range, lng_range) = lat_lng_range
    n_bits = 5
    bits = 0b00000
    for i_bits in range(n_bits):
        if (i_chars * n_bits + i_bits) % 2 == 0:
            # lng
            if lng < mid(lng_range):
                #bits |=( 0b0000 >> i_bits)
                lng_range = lower_half(lng_range)
            else:
                bits |= (0b10000 >> i_bits)
                lng_range = upper_half(lng_range)
        else:
            # lat
            if lat < mid(lat_range):
                #bits |=( 0b0000 >> i_bits)
                lat_range = lower_half(lat_range)
            else:
                bits |= (0b10000 >> i_bits)
                lat_range = upper_half(lat_range)
    return (bits2char(bits), (lat_range, lng_range))

# encode()
def encode(lat, lng, n_chars=11):
    chars = ''
    lat_lng_range = ((-90.0, +90.0), (-180.0, +180.0))
    for i_chars in range(n_chars):
        (char, lat_lng_range) = get_char(i_chars, (lat, lng), lat_lng_range)
        chars += char
    return chars

# decode()
def decode(geohash):
    lat_range = (-90.0, +90.0)
    lng_range = (-180.0, +180.0)
    for (i_chars, char) in enumerate(geohash):
        bits = char2bits(char)
        n_bits = 5
        for i_bits in range(n_bits):
            masked = bits & (0b10000 >> i_bits)
            if (i_chars * n_bits + i_bits) % 2 == 0:
                # lng
                if masked == 0:
                    lng_range = lower_half(lng_range)
                else:
                    lng_range = upper_half(lng_range)
            else:
                # lat
                if masked == 0:
                    lat_range = lower_half(lat_range)
                else:
                    lat_range = upper_half(lat_range)
    return (lat_range, lng_range)

# decode_to_range()
def decode_to_range(geohash):
    return decode(geohash)

# decode_to_point()
def decode_to_point(geohash):
    (lat_range, lng_range) =  decode(geohash)
    return (mid(lat_range), mid(lng_range))

# get_longest_geohash()
def get_longest_geohash(lat_lng_range, n_chars=11):
    ((minlat, maxlat), (minlng, maxlng)) = lat_lng_range
    (lat, lng) = ((minlat + maxlat) / 2, (minlng + maxlng) / 2)
    chars = ''
    lat_lng_range1 = ((-90.0, +90.0), (-180.0, +180.0))
    for i_chars in range(n_chars):
        (char1, lat_lng_range2) = get_char(
            i_chars, (lat, lng), lat_lng_range1)
        if is_contained(lat_lng_range, lat_lng_range2):
            chars += char1
            lat_lng_range1 = lat_lng_range2
        else:
            break
    return chars

# get_sub_geohashes()
def get_sub_geohashes(geohash):
    # TODO: efficient way: dont use decode().
    return [(geohash, decode(geohash)) for geohash in [
        geohash + c for c in BASE32
    ]]

if __name__ == "__main__":
    # encode
    print(encode(34.35067, 134.04692))
    assert(encode(24.44944, 122.93361) == 'wsr7j6vs29z')
    assert(encode(20.42527, 136.06972) == 'x58u0q6cy63')
    assert(encode(24.28305, 153.98638) == 'xkmd0h97n8x')
    assert(encode(45.55722, 148.75222) == 'z21g0vqn1cq')
    assert(encode(35.68123, 139.76712) == 'xn76urx61zq')
    assert(encode(35.68123, 139.76712, 1) == 'x')
    assert(encode(35.68123, 139.76712, 10) == 'xn76urx61z')
    # decode
    (lat_range, lng_range) = decode('xn76urx61zq')
    assert(lat_range[0] <= 35.68123 and 35.68123 < lat_range[1])
    assert(lng_range[0] <= 139.76712 and 139.76712 < lng_range[1])
    # get_longest_geohash
    assert(get_longest_geohash(((35.0, 36.0), (139.0, 140.0))) == 'xn')
    assert(get_longest_geohash(((24.449, 24.450), (122.933, 122.934))) == 'wsr7j6v')
    print('TEST: OK')
