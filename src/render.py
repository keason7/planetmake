"""Classes used to create window and render 3D object(s)."""

import pygame
from OpenGL.GL import (
    GL_AMBIENT,
    GL_DEPTH_TEST,
    GL_DIFFUSE,
    GL_FRONT,
    GL_LIGHT0,
    GL_LIGHTING,
    GL_MODELVIEW,
    GL_POSITION,
    GL_PROJECTION,
    GL_SHININESS,
    GL_SPECULAR,
    GL_TEXTURE_2D,
    glClearColor,
    glEnable,
    glLightfv,
    glLoadIdentity,
    glMaterialfv,
    glMatrixMode,
)
from OpenGL.GLU import gluLookAt, gluPerspective
from pygame.locals import DOUBLEBUF, OPENGL, QUIT


class Camera:
    """OpenGL Camera."""

    def __init__(self, window_width, window_height):
        """Initialize camera.

        Args:
            window_width (int): Width of the window (pixels).
            window_height (int): Height of the window (pixels).
        """
        self.window_width = window_width
        self.window_height = window_height

    def set_shading(self):
        light_pos = [1.0, 0.5, 1.0, 0.0]
        light_color = [1.0, 1.0, 1.0, 1.0]
        ambient_light = [0.2, 0.2, 0.2, 1.0]

        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_color)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_color)
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)

        mat_diffuse = [1.0, 1.0, 1.0, 1.0]
        mat_specular = [1.0, 1.0, 1.0, 1.0]
        mat_shininess = [50.0]

        glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)

    def set_at(self, eye_x, eye_y, eye_z, center_x, center_y, center_z, up_x, up_y, up_z):
        """Set the camera's position and orientation.

        Args:
            eye_x (float): X coordinate of the camera position.
            eye_y (float): Y coordinate of the camera position.
            eye_z (float): Z coordinate of the camera position.
            center_x (float): X coordinate of the point the camera is looking at.
            center_y (float): Y coordinate of the point the camera is looking at.
            center_z (float): Z coordinate of the point the camera is looking at.
            up_x (float): X component of the up vector.
            up_y (float): Y component of the up vector.
            up_z (float): Z component of the up vector.
        """
        # set the background clear color
        glClearColor(0.0, 0.0, 0.0, 1.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.window_width / self.window_height), 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, up_x, up_y, up_z)


class Window:
    """Class used to create window and render planet."""

    def __init__(self, width=1400, height=1000):
        """Initialize render object."""
        pygame.init()
        self.width, self.height = width, height

        # create OpenGL window
        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        self.cam = Camera(self.width, self.height)

    def render(self, planet, speed=0.01):
        """Render loop."""
        # set camera viewpoint
        self.cam.set_shading()
        self.cam.set_at(0, -3, 2, 0, 0, 0, 0, 1, 0)

        clock = pygame.time.Clock()
        is_running = True
        rot_z = 0

        while is_running:
            # speed degrees per millisecond
            rot_z += speed * clock.tick(60)

            for event in pygame.event.get():
                if event.type == QUIT:
                    is_running = False

            planet.draw_and_rotate(rot_z, 0, 0, 1)
            pygame.display.flip()

        pygame.quit()
