# rg-ksj
Reverse Geocoding Database for Japan using KSJ (国土数値情報).
## TODO
- sample web page (for demo, test)
  - unmanaged
    - back: gcp, apache, slimphp.
    - front: gh pages, js, OSM.
  - managed
    - back: cloud NoSQL DB with JSON support.
    - front: same as unmanaged.
- area code -> area name 
- debug
  43.05753 142.65566
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
