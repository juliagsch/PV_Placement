import numpy as np
import trimesh
import os
from scipy.spatial import ConvexHull

from shapely.geometry import Polygon, Point

class PolygonInfo:
    polygon: Polygon
    normal: np.ndarray


def similar_normals(n1, n2, tol=0.25):
    n1 = n1 / np.linalg.norm(n1)
    n2 = n2 / np.linalg.norm(n2)
    dot = np.dot(n1, n2)
    dot = max(min(dot, 1.0), -1.0)
    angle = np.arccos(abs(dot))  # note abs() here!
    # print(n1, n2, angle)
    return angle < tol 

def get_xyz_file(x_center, y_center, patch_size):
    files = [f for f in os.listdir("./tiles/area/") if f.endswith('.xyz')]
    radius = patch_size/2

    out = []
    for file in files:
        try:
            parts = file.split('_')
            x_min = float(parts[0])
            y_min = float(parts[1])
            x_max = float(parts[2])
            y_max = float(parts[3])

            if x_min <= x_center+radius <= x_max and y_min <= y_center+radius <= y_max:
                out.append(f"./tiles/area/{file}")
            elif x_min <= x_center+radius <= x_max and y_min <= y_center-radius <= y_max:
                out.append(f"./tiles/area/{file}")
            elif x_min <= x_center-radius <= x_max and y_min <= y_center-radius <= y_max:
                out.append(f"./tiles/area/{file}")
            elif x_min <= x_center-radius <= x_max and y_min <= y_center+radius <= y_max:
                out.append(f"./tiles/area/{file}")

        except Exception as e:
            print(f"Skipping file {file} due to error: {e}")
    
    return out


def generate_surroundings(input_paths, center_x, center_y, out_path, patch_size=50, spacing=0.5, min_z=0):
    radius = patch_size/2

    # Store points in a grid dict
    grid = {}
    for input_path in input_paths:
        with open(input_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                try:
                    x, y, z = map(float, line.strip().split())
                    if abs(x - center_x) <= radius and abs(y - center_y) <= radius:
                        grid[(round(x, 2), round(y, 2))] = z
                except ValueError:
                    continue

    # Create grid around center of dimensions size / spacing
    grid_size = int(patch_size /spacing)
    z_grid = np.full((grid_size, grid_size), np.nan)

    for (x, y), z in grid.items():
        i = int((y - (center_y - radius)) / spacing)
        j = int((x - (center_x - radius)) / spacing)
        if 0 <= i < grid_size and 0 <= j < grid_size:
            z_grid[i, j] = z

    np.savetxt(os.path.join(out_path,'surroundings2D.csv'), z_grid, delimiter=",", fmt="%.2f")

    xs = sorted(set(x for x, y in grid))
    ys = sorted(set(y for x, y in grid))

    x_to_idx = {x: i for i, x in enumerate(xs)}
    y_to_idx = {y: i for i, y in enumerate(ys)}

    n_rows, n_cols = len(ys), len(xs)
    index_grid = -np.ones((n_rows, n_cols), dtype=int)
    vertices = []

    # Create vertex list and index grid
    height_mask = []
    idx = 1
    for (x, y), z in grid.items():
        i = y_to_idx[y]
        j = x_to_idx[x]
        index_grid[i, j] = idx
        vertices.append(f"v {x} {y} {z}")
        height_mask.append(z > min_z)
        idx += 1
    
    # Generate face list
    faces = []
    for i in range(0, n_rows - 1):
        for j in range(0, n_cols - 1):
            v1 = index_grid[i, j]
            v2 = index_grid[i, j+1]
            v3 = index_grid[i+1, j+1]
            v4 = index_grid[i+1, j]
            if v1 > 0 and v2 > 0 and v3 > 0 and v4 > 0:
                if height_mask[v1-1] and height_mask[v2-1] and height_mask[v3-1] and height_mask[v4-1]:
                    faces.append(f"f {v1} {v2} {v3} {v4}")

    with open(os.path.join(out_path,'surroundings3D.obj'), 'w') as out:
        out.write("\n".join(vertices) + "\n")
        out.write("\n".join(faces) + "\n")


def generate_mask(path):
    # Load meshes
    surrounding_mesh = trimesh.load(os.path.join(path, "surroundings3D.obj"), process=True)
    roof_mesh = trimesh.load(os.path.join(path, "roof.obj"), process=True)

    # Extract vertices from surroundings mesh
    vertices = surrounding_mesh.vertices
    x_vals = np.unique(np.round(vertices[:, 0], 2))
    y_vals = np.unique(np.round(vertices[:, 1], 2))

    x_to_idx = {v: i for i, v in enumerate(x_vals)}
    y_to_idx = {v: i for i, v in enumerate(y_vals)}

    n_rows = len(y_vals)
    n_cols = len(x_vals)

    # Create empty mask
    roof_mask = np.zeros((n_rows, n_cols), dtype=np.uint8)

    # Loop over each face in the roof mesh and mark where it intersects
    for face in roof_mesh.faces:
        poly_points = roof_mesh.vertices[face][:, :2]  # x, y
        polygon = Polygon(poly_points)
        
        if not polygon.is_valid or polygon.area == 0:
            continue

        # Get bounding box in x/y coordinates to reduce checks
        minx, miny, maxx, maxy = polygon.bounds

        x_range = x_vals[(x_vals >= minx) & (x_vals <= maxx)]
        y_range = y_vals[(y_vals >= miny) & (y_vals <= maxy)]

        for y in y_range:
            for x in x_range:
                if polygon.contains(Point(x, y)):
                    i = y_to_idx[y]
                    j = x_to_idx[x]
                    roof_mask[i, j] = 1

    # Save the mask
    np.savetxt(os.path.join(path, "mask.csv"), roof_mask, delimiter=",", fmt="%d")
