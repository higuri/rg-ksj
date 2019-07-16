// index.js
// Note:
// - 'L' is imported from leaflet.js in index.html
// - 'decodeToCorners()' is imported from geohash.js in index.html

let map;

// API_URL: https://YOUR-DOMAIN/api/v1
const API_URL = 'https://example01.tk/api/v1/';

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
  show(latlng=null, zoom=5) {
    if (latlng == null) {
      // Tokyo Station.
      latlng = [35.68123, 139.76712];
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
      let areaName = 'N/A';
      if (xhr.readyState == 4 && xhr.status == '200') {
        if (result.area_name !== '') {
          areaName = result.area_name;
        }
      } else {
        console.error('error');
      }
      this.popup
        .setLatLng(latlng)
        //.setContent(`${latlng.lat}, ${latlng.lng}: ${areaCode}`)
        .setContent(`${areaName}`)
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
