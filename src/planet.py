"""Planet class."""

from OpenGL.GL import GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glClear, glPopMatrix, glPushMatrix, glRotatef
from OpenGL.GLU import gluNewQuadric, gluSphere


class Planet:
    """A class representing a 3D textured sphere (planet) using OpenGL."""

    def __init__(self, radius, slices, stacks):
        """_summary_

        Args:
            radius (float): Radius of the sphere.
            slices (int): Number of vertical divisions (longitude).
            stacks (int): Number of horizontal divisions (latitude).
        """
        self.radius = radius
        self.slices = slices
        self.stacks = stacks

    def __draw(self):
        """Draw geometry."""
        quad = gluNewQuadric()
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
