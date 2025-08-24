"""Utility functions."""

import random

import numpy as np


def hex2rgba(hexa):
    """Convert hexadecimal color to RGBA format.

    Args:
        hexa (str): Input hexa color.

    Raises:
        ValueError: Invalid hexadecimal color.

    Returns:
        tuple: RGBA color in tuple(r, g, b, a) format.
    """
    hexa = hexa.lstrip("#")

    if len(hexa) == 6:
        r, g, b = (int(hexa[i : i + 2], 16) for i in (0, 2, 4))
        a = 255
    elif len(hexa) == 8:
        r, g, b, a = (int(hexa[i : i + 2], 16) for i in (0, 2, 4, 6))
    else:
        raise ValueError(f"Invalid hexadecimal color: {hexa}")

    return (r, g, b, a)


def random_seed(seed_min=0, seed_max=2**32):
    """Get a random seed between in [seed_min, seed_max] range.

    Args:
        seed_min (int, optional): Minimum value. Defaults to 0.
        seed_max (int, optional): Maximum value. Defaults to 2**32.

    Returns:
        int: Random seed.
    """
    return random.randint(int(seed_min), int(seed_max))


def get_latitude_grid(height, width):
    """Return latitudes as a map grid.

    Args:
        height (int): Map height.
        width (int): Map width.

    Returns:
        np.array: Numpy array of latitudes of shape (height, width).
    """
    # array 1D of [0, 1, ..., height-1]
    i = np.arange(height)
    # compute latitudes: top rows = 90, middel = 0, bottom rows = -90
    lat_1d = 90.0 - (i / (height - 1)) * 180.0
    # tile it as a grid
    return np.tile(lat_1d[:, None], (1, width))
