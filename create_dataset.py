""" 
Creates a dataset consisting of building patches in Switzerland. 

One sample consists of a folder named {lon_min}_{lat_min}_{lon_max}_{lat_max} where min and max mark the bounds of the patch.

The folder consists of:
-   roof.obj file representing the building's roof as a mesh
-   surroundings3D.obj file representing the surroundings of the building as a mesh. This is used by the simulator.
    Faces lower than the building roof are not represented as they are irrelevant for shading.
-   surroundings2D.csv file representing a grid of elevation points of the patch. This could be used for model training.
-   mask.csv file representing a mask of the surroundings grid indicating which points correspond to the roof. Could also be used for model training.

Important: Coordinates are provided in LV95 format (Swiss Coordinate System).
If you would like to view buildings on maps, please convert them to GPS coordinates using 
https://www.swisstopo.admin.ch/en/coordinates-conversion-navref

In our format, the x axis represents longitude, y axis represents latitude and the z axis represents elevation.
"""

import os
import shutil

from get_building import extract_buildings_from_gml, get_minmax, get_mesh, merge_faces, save_as_obj
from get_surroundings import get_xyz_file, generate_surroundings, generate_mask


building_size_min, building_size_max = 4, 40 # Size in m which a building should not exceed on either x or y axis.
patch_dimensions = 50 # Dimensions in m on x and y axis of generated patches


def process_tile(gml_file, out_path):
    buildings = extract_buildings_from_gml(gml_file)

    for i, roof_polygons in enumerate(buildings):
        min_x, min_y, max_x, max_y = get_minmax(roof_polygons)

        # Skip large buildings
        if max_x-min_x > building_size_max or max_y-min_y > building_size_max:
            continue
        # Skip small buildings
        if max_x-min_x < building_size_min or max_y-min_y < building_size_min:
            continue

        dir_name = os.path.join(out_path, f'{min_x}_{min_y}_{max_x}_{max_y}')
        print("Processing sample: ", dir_name)
        # Remove old files and recreate directory
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
        os.makedirs(dir_name, exist_ok=True)

        try:
            # Save roof with merged faces if similar normals and common edge
            vertices, faces = get_mesh(polygons=roof_polygons)
            faces = merge_faces(vertices, faces) # Needed for the simulator to run properly
            save_as_obj(vertices, faces, os.path.join(dir_name,'roof.obj'))

            # Get the surroundings of the house to compute shading
            center_x, center_y = (max_x + min_x) / 2, (max_y + min_y) / 2
            tile_filenames = get_xyz_file(center_x, center_y, patch_size=patch_dimensions)
            generate_surroundings(tile_filenames, center_x, center_y, patch_size=patch_dimensions, out_path=dir_name)

            # Save mask indicating where on path the roof is located
            generate_mask(dir_name)
        except:
            print('Failed to process ', dir_name)
            shutil.rmtree(dir_name)



def get_gml_files():
    return [f"./tiles/buildings/{f}" for f in os.listdir(f"./tiles/buildings/") if f.endswith('.gml')]

if __name__ == '__main__':
    tiles = get_gml_files()
    out_path = './out'
    os.makedirs(out_path, exist_ok=True)

    for tile in tiles:
        process_tile(tile, out_path)