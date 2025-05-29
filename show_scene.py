
import trimesh
from utils import get_building_filenames
import random

filenames = get_building_filenames()
idx = random.randint(0, len(filenames)-1)
filename = filenames[idx]
print(filename)

mesh1 = trimesh.load(f"./surroundings3D/{filename}")
mesh2 = trimesh.load(f"./roofs_poly/{filename}")
mesh1.merge_vertices()
mesh1.remove_degenerate_faces()
mesh1.remove_duplicate_faces()
mesh2.merge_vertices()
mesh2.remove_degenerate_faces()
mesh2.remove_duplicate_faces()

scene = trimesh.Scene()
scene.add_geometry(mesh1)
scene.add_geometry(mesh2)

# Show the scene
scene.show()
