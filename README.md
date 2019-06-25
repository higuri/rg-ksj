# rg-ksj
Reverse Geocoding Database for Japan using KSJ (国土数値情報).
## TODO
- sample web page (for demo, test)
- area code -> area name 
- debug
  43.05753 142.65566
- write README
  - how to build
  - KSJ link, license
  - figure: geohash on map -> (json, fs, cdb)
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
