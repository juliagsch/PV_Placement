import numpy as np
import trimesh

file_path = "./tiles/area/ruettenen_points.xyz"
points = np.loadtxt(file_path, skiprows=1)

point_cloud = trimesh.points.PointCloud(points)
point_cloud.show()
