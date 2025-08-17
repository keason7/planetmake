import random

import numpy as np

from src.perlin import perlin_noise
from src.utils import hex2rgb

_colors = {
    "ice": "#ffffff",
    "ocean": "#5169a5",
    "deep_ocean": "#182a60",
    "desert": "#e5bb99",
    "ground": "#948c7d",
    "forest": "#647860",
    "dark_forest": "#385339",
}


def compute_lat_lon(i, j, shape):
    lat = 90.0 - (i / shape) * 180.0
    lon = (j / shape) * 360.0 - 180.0

    return lat, lon


def biome_color(altitude, biome):
    sea_level = 0.6

    if altitude < sea_level:
        if altitude < sea_level * (8 / 10):
            return hex2rgb(_colors["deep_ocean"])

        return hex2rgb(_colors["ocean"])

    else:

        if biome < 0.2:
            return hex2rgb(_colors["ground"])

        if biome < 0.35:
            return hex2rgb(_colors["desert"])

        if biome < 0.6:
            return hex2rgb(_colors["forest"])

        return hex2rgb(_colors["dark_forest"])


def random_seed(seed_min=0, seed_max=2**32):
    return random.randint(int(seed_min), int(seed_max))


def generate_noise(shape, res, octaves=6, persistence=0.55, lacunarity=2.0, tileable=(True, True), seed=None):
    if seed is None:
        seed = random_seed()

    noise_map = perlin_noise((shape, shape), (res, res), octaves, persistence, lacunarity, tileable, seed)
    return (noise_map - np.min(noise_map)) / (np.max(noise_map) - np.min(noise_map))


def generate_texture(shape=1024, res=8):
    texture = np.zeros((shape, shape, 3), dtype=np.uint8)

    altitude_map = generate_noise(shape, res, seed=2079352251)
    biome_map = generate_noise(shape, res, seed=2074168408)

    for i in range(shape):
        for j in range(shape):
            lat, lon = compute_lat_lon(i, j, shape)
            texture[i, j] = biome_color(altitude_map[i, j], biome_map[i, j])

    return texture
