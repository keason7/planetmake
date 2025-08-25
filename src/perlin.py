"""Perlin noise implementation.

MIT Licensed code from: https://github.com/pvigier/perlin-numpy
Original author: Pierre Vigier
Commit: 5e26837db14042e51166eb6cad4c0df2c1907016
License: MIT License

This file contains Perlin noise functions adapted for this project.
"""

import numpy as np


def _fade(t):
    """Smoothstep function used in Perlin noise interpolation.

    Args:
        t (np.array): Input array.

    Returns:
        np.array: Smoothed array.
    """
    return t * t * t * (t * (t * 6 - 15) + 10)


def _perlin_2d(shape, res, tileable=(False, False), seed=42):
    """Generate single octave perlin noise.

    Args:
        shape (tuple): Output array shape (height, width)
        res (tuple): Base resolution of noise (cells along each axis).
        tileable (tuple, optional): Make noise tilable along an axis (avoid begin/end discontinuity).
            Defaults to (False, False).
        seed (int, optional): Random seed. Defaults to 42.

    Returns:
        np.array: Single octaves perlin noise of 2D shape.
    """
    np.random.seed(seed)

    # compute the step size for interpolation between grid points
    delta = (res[0] / shape[0], res[1] / shape[1])

    # compute number of grid points along each axis
    d = (shape[0] // res[0], shape[1] // res[1])

    # create a grid of point offset coordinates of shape (height, width, 2) with values in [0,1) range
    # each point has a x and y offset inside its cell so grid give the relative position vector from
    # the top-left corner of the current cell
    grid = np.mgrid[0:res[0]:delta[0], 0:res[1]:delta[1]]
    grid = np.transpose(grid, (1, 2, 0)) % 1

    # generate random gradients vectors for each grid coordinate
    # random angles between in [0, 2π] range as unit vectors with cos/sin
    angles = 2 * np.pi * np.random.rand(res[0] + 1, res[1] + 1)
    gradients = np.dstack((np.cos(angles), np.sin(angles)))

    # if tiling copy last row/col to avoid discontinuity
    if tileable[0]:
        gradients[-1, :] = gradients[0, :]
    if tileable[1]:
        gradients[:, -1] = gradients[:, 0]

    # repeat gradients to match the shape of the output grid
    gradients = gradients.repeat(d[0], 0).repeat(d[1], 1)

    # get vectors at each grid corners
    gradient_top_left = gradients[:-d[0], :-d[1]]
    gradient_bottom_left = gradients[d[0]:, :-d[1]]
    gradient_top_right = gradients[:-d[0], d[1]:]
    gradient_bottom_right = gradients[d[0]:, d[1]:]

    # compute dot product of gradient and vector from corners
    # represent how much each corner pulls the value at the point inside the cell
    dot_top_left = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1])) * gradient_top_left, 2)
    dot_bottom_left = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1])) * gradient_bottom_left, 2)
    dot_top_right = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1] - 1)) * gradient_top_right, 2)
    dot_bottom_right = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1] - 1)) * gradient_bottom_right, 2)

    # interpolate to find perlin noise values for (height, width) grid
    smoothed_grid = _fade(grid)
    n0 = dot_top_left * (1 - smoothed_grid[:, :, 0]) + smoothed_grid[:, :, 0] * dot_bottom_left
    n1 = dot_top_right * (1 - smoothed_grid[:, :, 0]) + smoothed_grid[:, :, 0] * dot_bottom_right

    return np.sqrt(2) * ((1 - smoothed_grid[:, :, 1]) * n0 + smoothed_grid[:, :, 1] * n1)


def perlin_noise_2d(shape, res, octaves=1, persistence=0.5, lacunarity=2.0, tileable=(False, False), seed=42):
    """Generate multiple octaves perlin noise.

    Args:
        shape (tuple): Output array shape (height, width)
        res (tuple): Base resolution of noise (cells along each axis).
        octaves (int, optional): Number of perlin noises to sum. Defaults to 1.
        persistence (float, optional): Amplitude multiplier for each successive octave. Defaults to 0.5.
        lacunarity (float, optional): Frequency multiplier for each successive octave. Defaults to 2.
        tileable (tuple, optional): Make noise tilable along an axis (avoid begin/end discontinuity).
            Defaults to (False, False).
        seed (int, optional): Random seed. Defaults to 42.

    Returns:
        np.array: Multiple octaves perlin noise of 2D shape.
    """
    noise = np.zeros(shape)

    # multipliers for each octave
    frequency, amplitude = 1, 1

    # sum multiple octaves of perlin noise
    for _ in range(octaves):
        noise += amplitude * _perlin_2d(shape, (int(frequency * res[0]), int(frequency * res[1])), tileable, seed)

        # update multipliers values
        frequency *= lacunarity
        amplitude *= persistence

    return noise
