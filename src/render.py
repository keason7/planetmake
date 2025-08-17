"""Classes used to create window and render 3D object(s)."""

import pygame
from OpenGL.GL import GL_DEPTH_TEST, GL_TEXTURE_2D, glClearColor, glEnable
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

        # switch to projection matrix mode to define the camera projection
        # glMatrixMode(GL_PROJECTION)
        # Define the projection (FOV, aspect ratio, near and far clipping planes)
        gluPerspective(45, (self.window_width / self.window_height), 0.1, 100.0)

        # switch back to modelview matrix to apply transformations
        # glMatrixMode(GL_MODELVIEW)
        # set the camera's position and orientation
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

        self.cam = Camera(self.width, self.height)

    def render(self, planet, speed=0.01):
        """Render loop."""
        # set camera viewpoint
        self.cam.set_at(0, 5, 3, 0, 0, 0, 0, 0, 1)

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
