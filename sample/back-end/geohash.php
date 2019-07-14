<?php
// geohash.php
// - encode (lat,lng) to geohash.
// - decode geohash to [lat_range,lng_range].
// Geohash:
// https://en.wikipedia.org/wiki/Geohash

// TODO: namespace

$BASE32 = str_split("0123456789bcdefghjkmnpqrstuvwxyz");
$BASE32_TO_DECIMAL = array_reduce(
    range(0, count($BASE32) - 1), function ($result, $i) use ($BASE32) {
        $c = $BASE32[$i];
        $result[$c] = $i;
        return $result;
    }, array());
assert(count($BASE32) === 32);
assert(count($BASE32_TO_DECIMAL) === 32);

// bits2char($bits)
function bits2char($bits) {
    global $BASE32;
    return $BASE32[$bits];
}
// char2bits($char)
function char2bits($char) {
    global $BASE32_TO_DECIMAL;
    return $BASE32_TO_DECIMAL[$char];
}

// mid()
function mid($seq) {
    assert(count($seq) === 2);
    return ($seq[0] + $seq[1]) / 2.0;
}
// lower_half()
function lower_half($seq) {
    assert(count($seq) === 2);
    return array($seq[0], mid($seq));
}
// upper_half()
function upper_half($seq) {
    assert(count($seq) === 2);
    return array(mid($seq), $seq[1]);
}

// encode()
function encode($lat, $lng, $n_chars=11) {
    $chars = array();
    $lat_range = array(-90.0, +90.0);
    $lng_range = array(-180.0, +180.0);
    foreach (range(0, $n_chars - 1) as $i_chars) {
        $n_bits = 5;
        $bits = 0b00000;
        foreach (range(0, $n_bits - 1) as $i_bits) {
            if (($i_chars * $n_bits + $i_bits) % 2 === 0) {
                // lng
                if ($lng < mid($lng_range)) {
                    //bits |=( 0b0000 >> i_bits);
                    $lng_range = lower_half($lng_range);
                } else {
                    $bits |= (0b10000 >> $i_bits);
                    $lng_range = upper_half($lng_range);
                }
            } else {
                // lat
                if ($lat < mid($lat_range)) {
                    //bits |=( 0b0000 >> i_bits);
                    $lat_range = lower_half($lat_range);
                } else {
                    $bits |= (0b10000 >> $i_bits);
                    $lat_range = upper_half($lat_range);
                }
            }
        }
        array_push($chars, bits2char($bits));
    }
    return implode($chars);
}

// decode()
function decode($geohash) {
    $lat_range = array(-90.0, +90.0);
    $lng_range = array(-180.0, +180.0);
    foreach (str_split($geohash) as $i_chars => $char) {
        $bits = char2bits($char);
        $n_bits = 5;
        foreach (range(0, $n_bits - 1) as $i_bits) {
            $masked = $bits & (0b10000 >> $i_bits);
            if (($i_chars * $n_bits + $i_bits) % 2 === 0) {
                // lng
                if ($masked === 0) {
                    $lng_range = lower_half($lng_range);
                } else {
                    $lng_range = upper_half($lng_range);
                }
            } else {
                // lat
                if ($masked === 0) {
                    $lat_range = lower_half($lat_range);
                } else {
                    $lat_range = upper_half($lat_range);
                }
            }
        }
    }
    return array($lat_range, $lng_range);
}

// test
/*
assert(encode(24.44944, 122.93361) === "wsr7j6vs29z");
assert(encode(20.42527, 136.06972) === "x58u0q6cy63");
assert(encode(24.28305, 153.98638) === "xkmd0h97n8x");
assert(encode(45.55722, 148.75222) === "z21g0vqn1cq");
assert(encode(35.68123, 139.76712) === "xn76urx61zq");
assert(encode(35.68123, 139.76712, 1) === "x");
assert(encode(35.68123, 139.76712, 10) === "xn76urx61z");
list($lat_range, $lng_range) = decode("xn76urx61zq");
assert($lat_range[0] <= 35.68123 && 35.68123 < $lat_range[1]);
assert($lng_range[0] <= 139.76712 && 139.76712 < $lng_range[1]);
print("TEST: OK\n");
*/
