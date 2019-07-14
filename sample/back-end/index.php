<?php
// index.php

// TODO
header("Access-Control-Allow-Origin: *");

use \Psr\Http\Message\ServerRequestInterface as Request;
use \Psr\Http\Message\ResponseInterface as Response;

require __DIR__ . "/../vendor/autoload.php";
require __DIR__ . "/cdb.php";
require __DIR__ . "/geohash.php";

$GH2AC = __DIR__ . "/../lib/geohash2areacode.cdb";
$AC2AN = __DIR__ . "/../lib/areacode2name.cdb";

$app = new \Slim\App;

// get_area_from_cdb():
function get_area_from_cdb($lat, $lng) {
    global $GH2AC;
    global $AC2AN;
    $gh = encode($lat, $lng, 7);
    $ac = null;
    // gh2ac
    while (0 < strlen($gh)) {
        $ac = cdb_get($GH2AC, $gh);
        if ($ac !== null) {
            break;
        }
        $gh = substr($gh, 0, strlen($gh) - 1);
    }
    // ac2an
    if ($ac !== null) {
        $an = cdb_get($AC2AN, $ac);
        if ($an !== null) {
            return $an;
        }
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
            $area_name = get_area_from_cdb($lat, $lng);
            $result['lat'] = $latlng[0];
            $result['lng'] = $latlng[1];
            $result['area_name'] = $area_name;
        }
    }
    return $response->withJson($result, 200);
});
$app->run();
