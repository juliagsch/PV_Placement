import trimesh
import numpy as np
from lxml import etree
import os

def get_gml_files():
    return [f"./tiles/buildings/{f}" for f in os.listdir(f"./tiles/buildings/") if f.endswith('.gml')]

def parse_pos_list(pos_list_text):
    coords = list(map(float, pos_list_text.strip().split()))
    return np.array(coords).reshape((-1, 3))

def save_as_obj(polygons, types, output_path):
    vertices = []
    faces = []
    face_colors = []
    
    color_map = {
        'roof': [255, 0, 0, 255],
        'wall': [0, 255, 0, 255],
        'ground': [0, 0, 255, 255]
    }

    for poly, surface_type in zip(polygons, types):
        if len(poly) < 3:
            continue
        base_index = len(vertices)
        for v in poly:
            vertices.append(v)
        for i in range(1, len(poly) - 1):
            faces.append([base_index, base_index + i, base_index + i + 1])
            face_colors.append(color_map.get(surface_type, [200, 200, 200, 255]))

    if not vertices or not faces:
        return

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    mesh.visual.face_colors = np.array(face_colors)
    # Remove duplicates
    mesh.merge_vertices()
    mesh.remove_degenerate_faces()
    mesh.remove_duplicate_faces()
    mesh.export(output_path)

def extract_buildings_from_gml(gml_path):
    ns = {
        'gml': 'http://www.opengis.net/gml',
        'bldg': 'http://www.opengis.net/citygml/building/2.0'
    }

    tree = etree.parse(gml_path)
    buildings = []

    for building in tree.xpath('//bldg:Building', namespaces=ns):
        polygons = []
        types = []

        for roof in building.xpath('.//bldg:RoofSurface//gml:Polygon', namespaces=ns):
            pos_list = roof.xpath('.//gml:posList', namespaces=ns)
            if not pos_list:
                continue
            coords = parse_pos_list(pos_list[0].text)
            polygons.append(coords)
            types.append('roof')

        for wall in building.xpath('.//bldg:WallSurface//gml:Polygon', namespaces=ns):
            pos_list = wall.xpath('.//gml:posList', namespaces=ns)
            if not pos_list:
                continue
            coords = parse_pos_list(pos_list[0].text)
            polygons.append(coords)
            types.append('wall')

        if polygons:
            buildings.append((polygons, types))

    print(f"Found {len(buildings)} buildings")
    return buildings

def get_minmax(polygons):
    all_points = np.concatenate(polygons, axis=0)
    min_x, min_y = np.floor(np.min(all_points[:, :2], axis=0))
    max_x, max_y = np.ceil(np.max(all_points[:, :2], axis=0))
    return int(min_x), int(min_y), int(max_x), int(max_y)

if __name__ == "__main__":
    os.makedirs("buildings", exist_ok=True)
    os.makedirs("roofs", exist_ok=True)

    gml_file = "./tiles/buildings/attiswil.gml"
    buildings = extract_buildings_from_gml(gml_file)
    min_x_, min_y_, max_x_, max_y_ = np.inf, np.inf, 0, 0

    for i, (polygons, types) in enumerate(buildings):
        # Save full building
        min_x, min_y, max_x, max_y = get_minmax(polygons)
        min_x_ = min_x if min_x < min_x_ else min_x_
        min_y_ = min_y if min_y < min_y_ else min_y_

        max_x_ = max_x if max_x > max_x_ else max_x_
        max_y_ = max_y if max_y > max_y_ else max_y_

        filename = f"{min_x}_{min_y}_{max_x}_{max_y}_"
        save_as_obj(polygons, types, f"buildings/{filename}.obj")

        # Extract and save only roof
        roof_polys = [p for p, t in zip(polygons, types) if t == 'roof']
        roof_types = ['roof'] * len(roof_polys)
        save_as_obj(roof_polys, roof_types, f"roofs/{filename}.obj")
    print(min_x_, min_y_, max_x_, max_y_)