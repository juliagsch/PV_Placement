import numpy as np
import trimesh
import os
from utils import get_building_filenames

def get_xyz_file(x_center, y_center):
    files = [f for f in os.listdir("./tiles/area/") if f.endswith('.xyz')]

    for file in files:
        try:
            parts = file.split('_')
            x_min = float(parts[0])
            y_min = float(parts[1])
            x_max = float(parts[2])
            y_max = float(parts[3])

            if x_min <= x_center <= x_max and y_min <= y_center <= y_max:
                return f"./tiles/area/{file}"
        except Exception as e:
            print(f"Skipping file {file} due to error: {e}")
    
    return None

def generate_obj_from_xyz(input_path, output_path, center_x, center_y, radius=50, spacing=0.5):
    # Store filtered points in a grid dict
    grid = {}

    with open(input_path, 'r', encoding='utf-8-sig') as f:
        for line in f:
            try:
                x, y, z = map(float, line.strip().split())
                if abs(x - center_x) <= radius and abs(y - center_y) <= radius:
                    grid[(round(x, 2), round(y, 2))] = z
            except ValueError:
                continue

    xs = sorted(set(x for x, y in grid))
    ys = sorted(set(y for x, y in grid))

    x_to_idx = {x: i for i, x in enumerate(xs)}
    y_to_idx = {y: i for i, y in enumerate(ys)}

    n_rows, n_cols = len(ys), len(xs)
    index_grid = -np.ones((n_rows, n_cols), dtype=int)
    vertices = []
    idx = 1

    # Create vertex list and index grid
    for (x, y), z in grid.items():
        i = y_to_idx[y]
        j = x_to_idx[x]
        index_grid[i, j] = idx
        vertices.append(f"v {x} {y} {z}")
        idx += 1

    # Generate face list
    faces = []
    for i in range(n_rows - 1):
        for j in range(n_cols - 1):
            v1 = index_grid[i, j]
            v2 = index_grid[i, j+1]
            v3 = index_grid[i+1, j]
            v4 = index_grid[i+1, j+1]
            if v1 > 0 and v2 > 0 and v3 > 0 and v4 > 0:
                faces.append(f"f {v1} {v2} {v3} {v4}")

    with open(output_path, 'w') as out:
        out.write("\n".join(vertices) + "\n")
        out.write("\n".join(faces) + "\n")

    print(f"Wrote OBJ with {len(vertices)} vertices and {len(faces)} faces to {output_path}")

os.makedirs("surroundings3D", exist_ok=True)
os.makedirs("surroundings2D", exist_ok=True)

filenames = get_building_filenames()

for filename in filenames:
    building = trimesh.load(f"./buildings/{filename}")

    vertices = building.vertices

    max_x_house, min_x_house = max(vertices[:, 0]), min(vertices[:, 0])
    max_y_house, min_y_house = max(vertices[:, 1]), min(vertices[:, 1])
    min_z_house = min(vertices[:, 2])

    center_x, center_y = (max_x_house + min_x_house) / 2, (max_y_house + min_y_house) / 2
    tile_filename = get_xyz_file(center_x, center_y)

    generate_obj_from_xyz(tile_filename, f"./surroundings3D/{filename}", center_x, center_y)