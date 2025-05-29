import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import trimesh
import os

filename = "2611920_1235935_2611929_1235942_"
# Load building and roof
building = trimesh.load(f"./buildings/{filename}.obj")
roof = trimesh.load(f"./roofs_poly/{filename}.obj")

vertices = building.vertices

max_x_house, min_x_house = max(vertices[:, 0]), min(vertices[:, 0])
max_y_house, min_y_house = max(vertices[:, 1]), min(vertices[:, 1])
min_z_house = min(vertices[:, 2])

center_x, center_y = (max_x_house + min_x_house) / 2, (max_y_house + min_y_house) / 2
min_x_bb, max_x_bb = center_x - 50, center_x + 50
min_y_bb, max_y_bb = center_y - 50, center_y + 50

num_vertices = len(vertices)
new_vertices = np.array([
    [min_x_bb, min_y_bb, min_z_house],
    [max_x_bb, max_y_bb, min_z_house],
    [max_x_bb, min_y_bb, min_z_house],
    [min_x_bb, max_y_bb, min_z_house]
])

vertices_building = np.vstack((vertices, new_vertices))

faces = building.faces
new_faces = np.array([
    [num_vertices, num_vertices + 3, num_vertices + 2],
    [num_vertices + 1, num_vertices + 3, num_vertices + 2],
])
faces_building = np.vstack((faces, new_faces))


def get_xyz_file(center):
    x_center, _, y_center = center
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
            print(f"Skipping file {file} due to: {e}")
    
    return None


def center_vertices(vertices):
    swapped = [[x, z, y] for x, y, z in vertices]  # Z is up
    v = np.array(swapped)
    center = v.mean(axis=0)
    return (v - center).tolist(), center

def draw_surroundings(center):
    file = get_xyz_file(center)
    center_x,_, center_y = center

    if file:
        try:
            points = []

            with open(file, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    try:
                        x, y, z = map(float, line.strip().split())
                        if abs(x - center_x) <= 50 and abs(y - center_y) <= 50:
                            points.append([x, z, y])
                    except ValueError:
                        continue

            glBegin(GL_POINTS)
            glColor3f(0.6, 0.6, 0.6)
            for pt in points:
                glVertex3fv(pt)
            glEnd()

        except Exception as e:
            print(f"Failed to read or render surroundings: {e}")

def draw_mesh(vertices, faces):
    glBegin(GL_TRIANGLES)
    num_faces = len(faces)
    glColor3f(0.12, 0.12, 0.12)
    for i in range(num_faces - 2, num_faces):
        for idx in faces[i]:
            glVertex3fv(vertices[idx])
    glColor3f(0.2, 0.3, 0.7)
    for i in range(0, num_faces - 2):
        for idx in faces[i]:
            glVertex3fv(vertices[idx])
    glEnd()


def draw_mesh_roof(vertices, faces):
    glBegin(GL_TRIANGLES)
    glColor3f(0.7, 0.2, 0.2)
    for face in faces:
        for idx in face:
            glVertex3fv(vertices[idx])
    glEnd()


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 500.0)
    glTranslatef(0.0, 0.0, -50)

    centered_vertices_building, center = center_vertices(vertices_building)

    roof_swapped = np.array([[x, z, y] for x, y, z in roof.vertices])
    centered_vertices_roof = (roof_swapped - center).tolist()
    # draw_surroundings(center)

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glRotatef(1, 0, 1, 0)

        draw_mesh(centered_vertices_building, faces_building)
        draw_mesh_roof(centered_vertices_roof, roof.faces)

        pygame.display.flip()
        clock.tick(20)

if __name__ == "__main__":
    main()
