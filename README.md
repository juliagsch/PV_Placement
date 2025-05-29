## Creating building and roof meshes

1. Download .gml file from https://www.swisstopo.admin.ch/de/landschaftmodell-swissbuildings3d-3-0-beta
2. Run building_extractor.py
3. Run merge_objs.py. This will merge all buildings which are less than 3 m from eachother
4. Run remove_large.py to exclude buildings larger than 50 m on either the x or y axis
