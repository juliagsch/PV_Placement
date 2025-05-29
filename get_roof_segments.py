import trimesh
import numpy as np
import networkx as nx
from utils import get_roof_filenames

from shapely.geometry import Polygon
from sklearn.decomposition import PCA

filenames = get_roof_filenames()
# Load mesh
for filename in filenames:
    mesh = trimesh.load(f"./roofs/{filename}", force='mesh')

    normals = mesh.face_normals

    # Group faces based on normal similarity
    angle_tolerance = np.radians(1.0)
    adjacency = mesh.face_adjacency
    G = nx.Graph()
    G.add_nodes_from(range(len(mesh.faces)))

    for f1, f2 in adjacency:
        angle = np.arccos(np.clip(np.dot(normals[f1], normals[f2]), -1.0, 1.0))
        if angle < angle_tolerance:
            G.add_edge(f1, f2)

    components = list(nx.connected_components(G))

    face_areas = mesh.area_faces

    # Filter out components with 1 face and area < 1 square m
    filtered_components = []
    for comp in components:
        if len(comp) > 1:
            filtered_components.append(comp)
        else:
            face_idx = list(comp)[0]
            if face_areas[face_idx] >= 1.0:
                filtered_components.append(comp)

    vertices_per_face = mesh.vertices[mesh.faces]
    new_vertices = vertices_per_face.reshape(-1, 3)
    new_faces = np.arange(len(new_vertices)).reshape(-1, 3)

    all_faces = []
    all_vertices = []

    for comp in filtered_components:
        face_indices = list(comp)
        face_verts = mesh.vertices[mesh.faces[face_indices].reshape(-1)]
        unique_verts, _ = np.unique(face_verts, axis=0, return_inverse=True)

        if len(unique_verts) < 3:
            continue

        pca = PCA(n_components=2)
        verts_2d = pca.fit_transform(unique_verts)

        try:
            hull = Polygon(verts_2d).convex_hull
            if not hull.is_valid or hull.area == 0:
                continue

            coords_2d = np.array(hull.exterior.coords)[:-1]
            if len(coords_2d) < 3:
                continue

            coords_3d = pca.inverse_transform(coords_2d)
            start_idx = len(all_vertices)
            all_vertices.extend(coords_3d)
            all_faces.append([start_idx + i for i in range(len(coords_3d))])

        except Exception as e:
            print(f"Error in component: {e}")
    
    vertices = []
    faces = []

    for vertex in all_vertices:
        vertices.append(f"v {vertex[0]} {vertex[1]} {vertex[2]}")
    for face in all_faces:
        faces.append("f " + " ".join(str(idx + 1) for idx in face))
    
    with open(f"./roofs_poly/{filename}", 'w') as out:
        out.write("\n".join(vertices) + "\n")
        out.write("\n".join(faces) + "\n")
