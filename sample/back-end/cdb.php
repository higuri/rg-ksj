<?php
// cdb.php - PHP implementation of cdb [fetch(cdb_get) only].
//
// Note:
// If your PHP has the built-in support for cdb
// (configured with '--enable-dba' and '--with-cdb'),
// you do not need this script.
//

// TODO: namespace

// cdb_hash()
function cdb_hash($s) {
    return array_reduce(
        str_split($s),
        function ($h, $c) {
            return ((($h * 33) ^ ord($c)) & 0xffffffff);
        },
        5381);
}

// cdb_get()
function cdb_get($cdbpath, $key) {
    $retval = null;
    $fp = fopen($cdbpath, "rb");
    if ($fp) {
        $h = cdb_hash($key);
        fseek($fp, ($h % 256) * 8);
        extract(unpack("Lpcell/Lncells", fread($fp, 8)));
        if (0 < $ncells) {
            $start = ($h >> 8) % $ncells;
            for ($i = 0; $i < $ncells; $i++) {
                fseek($fp, $pcell + (($start + $i) % $ncells) * 8);
                extract(unpack("Lh1/Lp1", fread($fp, 8)));
                if ($p1 === 0) {
                    break;
                }
                if ($h1 === $h) {
                    fseek($fp, $p1);
                    extract(unpack("Lklen/Lvlen", fread($fp, 8)));
                    $k1 = fread($fp, $klen);
                    if ($k1 === $key) {
                        // return the first match.
                        $v1 = fread($fp, $vlen);
                        $retval = $v1;
                        break;
                    }
                }
            }
        }
        fclose($fp);
    }
    return $retval;
}
