"""Planet class."""

from OpenGL.GL import (GL_LINEAR, GL_RGBA, GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_TEXTURE_MIN_FILTER,
                       GL_UNSIGNED_BYTE, glBindTexture, glGenTextures, glPopMatrix, glPushMatrix, glRotatef,
                       glTexImage2D, glTexParameteri)
from OpenGL.GLU import gluNewQuadric, gluQuadricTexture, gluSphere


class Planet:
    """A class representing a 3D textured sphere (planet) using OpenGL."""

    def __init__(self, radius, texture):
        """Initialize planet.

        Args:
            radius (float): Radius of the sphere.
            texture (np.array): Planet texture of shape (H, W, 4).
        """
        height, width, _ = texture.shape

        self.radius = radius
        self.slices = height
        self.stacks = width

        self.texture = texture
        self.texture_id = None
        self.__load_texture()

    def __load_texture(self):
        """Load planet OpenGL texture."""
        # generate a new texture ID
        texture_id = glGenTextures(1)

        # bind texture so that next commands affect it
        glBindTexture(GL_TEXTURE_2D, texture_id)

        # generate texture image
        glTexImage2D(
            GL_TEXTURE_2D,  # define 2D texture target
            0,  # base value level = 0
            GL_RGBA,
            self.texture.shape[1],
            self.texture.shape[0],
            0,  # no image border
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            self.texture,
        )

        # apply filters if texture is larger/smaller that sphere (using linear interpolation)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        self.texture_id = texture_id

    def __draw(self):
        """Draw planet geometry and texture."""

        # bind planet texture so the sphere will use it
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        # create quadric object (helper to create spheres or cylinders)
        quad = gluNewQuadric()

        # enable texture and dra object
        gluQuadricTexture(quad, True)
        gluSphere(quad, self.radius, self.slices, self.stacks)

    def __rotate(self, angle, x, y, z):
        """Apply rotation on planet.

        Args:
            angle (float): Angle of rotation (degrees).
            x (float): Component x of the rotation axis.
            y (float): Component y of the rotation axis.
            z (float): Component z of the rotation axis.
        """
        glRotatef(angle, x, y, z)

    def draw_and_rotate(self, angle, x, y, z):
        """Draw and rotate planet.

        Args:
            angle (float): Angle of rotation (degrees).
            x (float): Component x of the rotation axis.
            y (float): Component y of the rotation axis.
            z (float): Component z of the rotation axis.
        """
        # save current transformation matrix
        glPushMatrix()

        # rotate and draw
        self.__rotate(angle, x, y, z)
        self.__draw()

        # restore the transformation matrix
        glPopMatrix()
