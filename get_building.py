import networkx as nx
import numpy as np
import trimesh

from lxml import etree


def parse_pos_list(pos_list_text):
    coords = list(map(float, pos_list_text.strip().split()))
    return np.array(coords).reshape((-1, 3))


def extract_buildings_from_gml(gml_path):
    """
    Extract a polygons from GML file for each available building.

    - gml_path: Path to GML file.
    """

    ns = {
        'gml': 'http://www.opengis.net/gml',
        'bldg': 'http://www.opengis.net/citygml/building/2.0'
    }

    tree = etree.parse(gml_path)
    buildings = []

    for building in tree.xpath('//bldg:Building', namespaces=ns):
        roof_polygons = []

        for roof in building.xpath('.//bldg:RoofSurface//gml:Polygon', namespaces=ns):
            pos_list = roof.xpath('.//gml:posList', namespaces=ns)
            if not pos_list:
                continue
            coords = parse_pos_list(pos_list[0].text)
            roof_polygons.append(coords)
    
        if roof_polygons:
            buildings.append(roof_polygons)

    print(f"Found {len(buildings)} buildings.")
    return buildings


def get_minmax(polygons):
    """ Get minimum and maximum x and y coordinates."""
    all_points = np.concatenate(polygons, axis=0)
    min_x, min_y = np.floor(np.min(all_points[:, :2], axis=0))
    max_x, max_y = np.ceil(np.max(all_points[:, :2], axis=0))
    return int(min_x), int(min_y), int(max_x), int(max_y)


def get_mesh(polygons):
    vertices = []
    faces = []

    for poly in polygons:
        if len(poly) < 3:
            continue
        face = []
        for v in poly:
            v = tuple(v.tolist()) 
            if v not in vertices:
                vertices.append(v)
                face.append(len(vertices))
            else:
                face.append(vertices.index(v)+1)
        faces.append(face[:3]) # face is given in format 1 2 3 1 and we only need 1 2 3

    return vertices, faces
    
    
def save_as_obj(vertices, faces, output_path):
    if not vertices or not faces:
        return
    
    with open(output_path, "w") as f:
        for v in vertices:
            f.write(
                f"v {v[0]} {v[1]} {v[2]}\n"
            )
        for face in faces:
            f.write("f {}\n".format(" ".join(map(str, face))))


def shared_edge(poly, tri):
    common = [v for v in poly if any(np.allclose(v, u) for u in tri)]
    if len(common) == 2:
        return common
    return None

def merge_faces(vertices, faces, angle_tolerance_degrees=2.0, min_area=1.0):
    """Unite faces with similar normals and vertices to convert triangular mesh to polygonal mesh."""
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=(np.array(faces)-1))
    normals = mesh.face_normals

    # Group faces based on normal similarity
    angle_tolerance = np.radians(angle_tolerance_degrees)
    adjacency = mesh.face_adjacency
    G = nx.Graph()
    G.add_nodes_from(range(len(mesh.faces)))

    for f1, f2 in adjacency:
        angle = np.arccos(np.clip(np.dot(normals[f1], normals[f2]), -1.0, 1.0))
        if angle < angle_tolerance:
            G.add_edge(f1, f2)

    components = list(nx.connected_components(G))

    face_areas = mesh.area_faces

    # Filter out components with 1 face and area < min_area square m
    filtered_components = []
    for comp in components:
        if len(comp) > 1:
            filtered_components.append(comp)
        else:
            face_idx = list(comp)[0]
            if face_areas[face_idx] >= min_area:
                filtered_components.append(comp)

    merged_faces = []

    for comp in filtered_components:
        face_indices = list(comp)
        merged = list(mesh.faces[face_indices[0]])
        remaining_faces = face_indices[1:]

        while remaining_faces:

            merged_this_round = False
            for face_idx in remaining_faces:
                face = mesh.faces[face_idx]
                common_edge = shared_edge(merged, list(face))  # should return two shared vertex indices

                if common_edge is not None:
                    # Find the vertex in the triangle that's NOT part of the common edge
                    not_common = [v for v in face if v not in common_edge]

                    if len(not_common) != 1:
                        raise Exception("Exactly one vertex should not be common when merging a triangle with a polygon")

                    # Insert the non-shared vertex into the merged polygon in the correct place
                    idx0 = merged.index(common_edge[0])
                    idx1 = merged.index(common_edge[1])

                    # Decide insertion point: after idx0 if idx1 == idx0+1 or after idx1 if idx0==idx1+1
                    if (idx1 - idx0) % len(merged) == 1:
                        insert_idx = idx1
                    else:
                        insert_idx = idx0
                    
                    # Handle case where vertex should be appended at the end of the list.
                    if idx1 == 0 and idx0!=1:
                        insert_idx = idx0+1
                    if idx0 == 0 and idx1!=1:
                        insert_idx = idx1+1

                    merged.insert(insert_idx, not_common[0])
                    remaining_faces.remove(face_idx)
                    merged_this_round = True
                    break

            if not merged_this_round:
                break
        
        merged_faces.append([m+1 for m in merged])
    return merged_faces