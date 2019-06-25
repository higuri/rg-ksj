<?php
// index.php
use \Psr\Http\Message\ServerRequestInterface as Request;
use \Psr\Http\Message\ResponseInterface as Response;

require __DIR__ . "/../vendor/autoload.php";

// http://example.com/35.12345+139.12345

$app = new \Slim\App;
$app->get('/[{latlng}]', function ($request, $response, $args) {
    $result = array();
    if (isset($args['latlng'])) {
        // TODO: '+' -> ' ' ?
        $latlng = explode(' ', $args['latlng']);
        if (1 < count($latlng)) {
            $result['lat'] = $latlng[0];
            $result['lng'] = $latlng[1];
            $result['area-code'] = '01234';
        }
    }
    return $response->withJson($result, 200);
});
$app->run();

