import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def load_obj_poly(filename):
    vertices = []
    faces = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):
                parts = line.strip().split()
                x, y, z = map(float, parts[1:4])
                vertices.append([x, y, z])
            elif line.startswith('f '):
                parts = line.strip().split()
                # OBJ faces can have formats like "f 1 2 3" or "f 1/1 2/2 3/3"

                face = []
                for p in parts[1:]:
                    idx = int(p.split('/')[0])  # vertex index (1-based)
                    face.append(idx)
                faces.append(face)

    return vertices, faces

def draw_faces(vertices, faces):
    for face in faces:
        glBegin(GL_POLYGON)
        for idx in face:
            v = vertices[idx - 1]
            glVertex3fv(v)
        glEnd()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(45, (display[0] / display[1]), 0.1, 1000.0)
    glTranslatef(0, 0, -100)

    vertices, faces = load_obj_poly("poly.obj")

    clock = pygame.time.Clock()
    angle = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glRotatef(1, 0, 1, 0)

        glColor3f(0.7, 0.7, 0.7)
        draw_faces(vertices, faces)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
