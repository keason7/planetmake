"""Planet class."""

from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_LINEAR,
    GL_RGB,
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_UNSIGNED_BYTE,
    glBindTexture,
    glClear,
    glGenTextures,
    glPopMatrix,
    glPushMatrix,
    glRotatef,
    glTexImage2D,
    glTexParameteri,
)
from OpenGL.GLU import gluNewQuadric, gluQuadricTexture, gluSphere


class Planet:
    """A class representing a 3D textured sphere (planet) using OpenGL."""

    def __init__(self, radius, slices, stacks, texture=None):
        """_summary_

        Args:
            radius (float): Radius of the sphere.
            slices (int): Number of vertical divisions (longitude).
            stacks (int): Number of horizontal divisions (latitude).
        """
        self.radius = radius
        self.slices = slices
        self.stacks = stacks

        self.texture = texture
        self.texture_id = None
        self.__load_texture()

    def __load_texture(self):
        texture_id = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, texture_id)

        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGB,
            self.texture.shape[1],
            self.texture.shape[0],
            0,
            GL_RGB,
            GL_UNSIGNED_BYTE,
            self.texture,
        )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        self.texture_id = texture_id

    def __draw(self):
        """Draw geometry."""
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        quad = gluNewQuadric()
        gluQuadricTexture(quad, True)
        gluSphere(quad, self.radius, self.slices, self.stacks)

    def __rotate(self, angle, x, y, z):
        """Apply rotation on geometry.

        Args:
            angle (float): Angle of rotation (degrees).
            x (float): Component x of the rotation axis.
            y (float): Component y of the rotation axis.
            z (float): Component z of the rotation axis.
        """
        glRotatef(angle, x, y, z)

    def draw_and_rotate(self, angle, x, y, z):
        """Draw and rotate sphere geometry.

        Args:
            angle (float): Angle of rotation (degrees).
            x (float): Component x of the rotation axis.
            y (float): Component y of the rotation axis.
            z (float): Component z of the rotation axis.
        """
        # clears the color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # save current transformation matrix
        glPushMatrix()
        # rotate and draw
        self.__rotate(angle, x, y, z)
        self.__draw()
        # restore the transformation matrix
        glPopMatrix()
