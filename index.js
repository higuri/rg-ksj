// index.js
// Note:
// - 'L' is imported from leaflet.js in index.html
// - 'decodeToCorners()' is imported from geohash.js in index.html

let map;

// const API_URL = 'http://example.com/api/v1/';
const API_URL = 'http://35.230.98.253/api/v1/';

/// OsmMap:
class OsmMap {

  // OsmMap()
  constructor(id) {
    // popup:
    this.popup = L.popup();
    // map:
    this.map = L.map(id);
    L.tileLayer(
      'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        attribution:
          '&copy; ' +
          '<a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
      })
      .addTo(this.map);
    this.map.on('click', (evt) => this.onMapClick(evt));
  }

  // show()
  show(latlng=null, zoom=3) {
    if (latlng == null) {
      latlng = [0.0, 0.0];
    }
    this.map.setView(latlng, zoom);
  }

  // getAreaCode()
  getAreaCode(latlng) {
    const url = API_URL + `${latlng.lat}+${latlng.lng}`;
    const xhr  = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.onload = (() => {
      const result = JSON.parse(xhr.responseText);
      let areaCode = 'N/A';
      if (xhr.readyState == 4 && xhr.status == '200') {
        areaCode = result.area_code;
      } else {
        console.error('error');
      }
      this.popup
        .setLatLng(latlng)
        //.setContent(`${latlng.lat}, ${latlng.lng}: ${areaCode}`)
        .setContent(`${areaCode}`)
        .openOn(this.map);
    });
    xhr.send(null);
  }

  // onMapClick()
  onMapClick(evt) {
    this.getAreaCode(evt.latlng);
  }
}

// main():
function main() {
  // map:
  map = new OsmMap('map');
  map.show();
}

// DOMContentLoaded:
window.addEventListener('DOMContentLoaded', () => {
  main();
});
