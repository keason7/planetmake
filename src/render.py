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

_cam_params = {
    "cam_eye": [0, -3, 2],
    "cam_center": [0, 0, 0],
    "cam_up": [0, 1, 0],
    "light_position": [1.0, 0.5, 1.0, 0.0],
    "light_color": [1.0, 1.0, 1.0, 1.0],
    "light_ambient_color": [0.2, 0.2, 0.2, 1.0],
    "material_diffuse": [1.0, 1.0, 1.0, 1.0],
    "material_specular": [1.0, 1.0, 1.0, 1.0],
    "material_shininess": [50.0],
}


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

        # enable OpenGL textures, lighning and depth buffer
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

    def set_shading(
        self,
        light_position,
        light_color,
        light_ambient_color,
        material_diffuse,
        material_specular,
        material_shininess,
    ):
        """Configure OpenGL lighting and material params for Phong-style shading.

        - Ambient lighting: Simulate existing light without any other light source to avoid completly dark scenes.
        - Diffuse lighting: Simulates the directional impact a light object has on an object.
        - Specular lighting: Simulates the bright spot of a light that appears on shiny objects.

        Args:
            light_position (list): Light coordinates [x, y, z, w]. If w=0, light is a direcional vector
                (infinite distance), and if w=1, light is set at a position (finite distance).
            light_color (list): Diffuse and specular color of the light [r, g, b, a].
            light_ambient_color (list): Ambient color of the light [r, g, b, a].
            material_diffuse (list): Diffuse reflectivity of the object material [r, g, b, a].
            material_specular (list): Specular reflectivity of the object material [r, g, b, a].
            material_shininess (list): Shininess coefficient of the material, controlling specular highlight size.
        """

        # define light coords
        # if w=0, the light is directional: the (x,y,z) vector defines its direction
        # if w=1, the light is positional: the (x,y,z) defines its location in world space
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)

        # sets diffuse, specular and ambient light colors
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_color)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_color)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient_color)

        # sets diffuse, specular and shininess material colors
        glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

    def set_at(self, eye, center, up):
        """Set the camera's position and orientation.

        Args:
            eye (list): Coordinates of the camera position.
            center (list): Coordinates of the point the camera is looking at.
            up (list): Components of the up vector to define camera orientation.
        """
        # set the background clear color
        glClearColor(0.0, 0.0, 0.0, 1.0)

        # switch to projection mode (camera lens params)
        glMatrixMode(GL_PROJECTION)
        # replace current proj matrix with identity matrix (avoid matrix multiplication)
        glLoadIdentity()
        # set projection matrix (fov, aspect ratio, near dist, far dist)
        gluPerspective(45, (self.window_width / self.window_height), 0.1, 100.0)

        # switch to the modelview mode (camera position/orientation)
        glMatrixMode(GL_MODELVIEW)
        # set view matrix
        gluLookAt(eye[0], eye[1], eye[2], center[0], center[1], center[2], up[0], up[1], up[2])


class Window:
    """Class used to create window and render planet."""

    def __init__(self, width=1400, height=1000):
        """Initialize render object.

        Args:
            width (int, optional): Width of the window (pixels). Defaults to 1400.
            height (int, optional): Height of the window (pixels). Defaults to 1000.
        """
        pygame.init()
        self.width, self.height = width, height

        # create OpenGL window
        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)

        # initialize OpenGL camera
        self.cam = Camera(self.width, self.height)

    def render(self, planet, delta_z=0.1):
        """Render loop.

        Args:
            planet (Planet): Planet object to render.
            delta_z (float, optional): Rotation degree shift by frame. Defaults to 0.1.
        """
        # set scene shading
        self.cam.set_shading(
            _cam_params["light_position"],
            _cam_params["light_color"],
            _cam_params["light_ambient_color"],
            _cam_params["material_diffuse"],
            _cam_params["material_specular"],
            _cam_params["material_shininess"],
        )
        # set camera viewpoint
        self.cam.set_at(_cam_params["cam_eye"], _cam_params["cam_center"], _cam_params["cam_up"])

        # clock for frame rate
        clock = pygame.time.Clock()

        rot_z = 0
        is_running = True

        while is_running:
            # define FPS limit
            clock.tick(60)

            # handle window closing
            for event in pygame.event.get():
                if event.type == QUIT:
                    is_running = False

            # rotate by delta_z degrees at each frame
            rot_z += delta_z
            planet.draw_and_rotate(rot_z, 0, 0, 1)

            # update display with new frame
            pygame.display.flip()

        pygame.quit()
