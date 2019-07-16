# rg-ksj
Reverse Geocoding Database for Japan based on KSJ (国土数値情報).

## Demo Page
https://higuri.github.io/rg-ksj/index.html

## TODO
- sample web page (for demo, test)
  - managed
    - back: cloud NoSQL DB with JSON support.
    - front: same as unmanaged.
  - [OK] unmanaged
    - back: apache, slimphp. [on GCP].
    - front: gh pages, js, OSM. [on gh-pages].
- argparse
- write README
  - how to build
  - KSJ link, license
  - figure: geohash on map -> (json, fs, cdb)
  - featues
    - stand alone (works without DBMS like PostgreSQL + PostGIS)
  - dbtype
    - fs
      - o unmanaged server or local machine.
      - o easy to implement (query).
      - x heavy storage use (especially n of files [inodes]).
    - cdb
      - o unmanaged server or local machine.
      - o low storage use.
      - x need cdb support to implement (query).
    - json
      - o managed server.
- [OK] speed-up (stop using in-review) [geohash-utils]
- [OK] debug 43.05753 142.65566
- [OK] area code -> area name 
