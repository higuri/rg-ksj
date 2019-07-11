<?php
// TODO
header("Access-Control-Allow-Origin: *");
// index.php
use \Psr\Http\Message\ServerRequestInterface as Request;
use \Psr\Http\Message\ResponseInterface as Response;

require __DIR__ . "/../vendor/autoload.php";
require __DIR__ . "/geohash.php";

$app = new \Slim\App;
$cdb_file = __DIR__ . "/../lib/area_code.cdb";

// cdb_get()
function cdb_get($key) {
    global $cdb_file;
    $dbid = dba_open($cdb_file, "r", "cdb");
    $val = dba_fetch($key, $dbid);
    dba_close($dbid);
    return $val === FALSE ? "" : $val;
}

// get_area_from_cdb():
function get_area_from_cdb($lat, $lng, $db_file) {
    $hash1 = encode($lat, $lng, 7);
    while (0 < count($hash1)) {
        $val = cdb_get($db_file, $hash1);
        if ($val !== "") {
            return $val;
        }
        $hash1 = substr($hash1, 0, count($hash1) - 1);
    }
    return "";
}

// http://example.com/api/v1/35.12345+139.12345
$app->get('/api/v1/{latlng}', function ($request, $response, $args) {
    $result = array();
    if (isset($args['latlng'])) {
        // TODO: '+' -> ' ' ?
        $latlng = explode(' ', $args['latlng']);
        if (1 < count($latlng)) {
            // TODO; check value.
            $lat = floatval($latlng[0]);
            $lng = floatval($latlng[1]);
            // $area_code = get_area_from_cdb($cdb_file, $lat, $lng);
            $area_code = '12345';
            $result['lat'] = $latlng[0];
            $result['lng'] = $latlng[1];
            $result['area_code'] = $area_code;
        }
    }
    return $response->withJson($result, 200);
});
$app->run();

