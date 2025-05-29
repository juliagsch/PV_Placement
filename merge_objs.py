import numpy as np
from scipy.spatial.distance import cdist
from utils import get_building_filenames
import os 

def get_minmax(vertices):
    min_x, min_y = np.floor(np.min(vertices[:, :2], axis=0))
    max_x, max_y = np.ceil(np.max(vertices[:, :2], axis=0))
    return int(min_x), int(min_y), int(max_x), int(max_y)

def load_obj(filename):
    vertices = []
    faces = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):
                vertices.append(list(map(float, line.strip().split()[1:4])))
            elif line.startswith('f '):
                face = [int(p.split('/')[0]) for p in line.strip().split()[1:]]
                faces.append(face)
    return np.array(vertices), faces

def write_obj(filename, vertices, faces):
    with open(filename, 'w') as f:
        for v in vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for face in faces:
            f.write("f " + " ".join(str(i) for i in face) + "\n")

def check_distance(dir, file1, file2, max_distance=3.0):
    v1, _ = load_obj(dir + file1)
    v2, _ = load_obj(dir + file2)

    # Compute pairwise distances between all vertices
    distances = cdist(v1[:, :3], v2[:, :3])
    min_distance = np.min(distances)

    if min_distance > max_distance:
        return False
    print(f"Minimum vertex-to-vertex distance: {min_distance:.2f} m {file1} {file2}")
    return True

def merge_objs(dir, file1, file2, outfile=""):
    v1, f1 = load_obj(dir + file1)
    v2, f2 = load_obj(dir + file2)

    merged_vertices = np.vstack((v1, v2))
    offset = len(v1)
    merged_faces = f1 + [[i + offset for i in face] for face in f2]
    
    if outfile == "":
        min_x, min_y, max_x, max_y = get_minmax(merged_vertices)
        outfile = f"{min_x}_{min_y}_{max_x}_{max_y}_.obj"
        
    write_obj(dir + outfile, merged_vertices, merged_faces)
    return outfile


while(True):
    filenames = get_building_filenames()
    num_files = len(filenames)
    num_merged = 0
    
    remove = []
    for idx1 in range(0, num_files-1):
        for idx2 in range(idx1+1, num_files):
            if not "./roofs/"+filenames[idx1] in remove and not "./roofs/"+filenames[idx2] in remove:
                if check_distance("./buildings/", filenames[idx1], filenames[idx2]):
                    outfile = merge_objs("./buildings/", filenames[idx1], filenames[idx2])
                    _ = merge_objs("./roofs/", filenames[idx1], filenames[idx2], outfile=outfile)

                    remove.append("./buildings/"+filenames[idx1])
                    remove.append("./roofs/"+filenames[idx1])
                    remove.append("./buildings/"+filenames[idx2])
                    remove.append("./roofs/"+filenames[idx2])
                    
                    num_merged+=1
                    print(outfile)
                    break
    
    for file in set(remove):
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed {file}.")
        else:
            print(f"File already removed or not found: {file}")

    print(f"Merged {num_merged} files.")
    if num_merged == 0:
        break
