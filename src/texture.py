import random

import numpy as np

from src.perlin import perlin_noise
from src.utils import hex2rgb

_colors = {
    "ground": "#a37e4d",
    "water": "#000063",
}


def biome_color(noise_val):
    if noise_val < 0.6:
        return hex2rgb(_colors["water"])

    return hex2rgb(_colors["ground"])


def random_seed(seed_min=0, seed_max=2**32):
    return random.randint(int(seed_min), int(seed_max))


def generate_noise(shape, res, octaves=6, persistence=0.55, lacunarity=2.0, tileable=(False, False), seed=None):
    if seed is None:
        seed = random_seed()

    noise_map = perlin_noise((shape, shape), (res, res), octaves, persistence, lacunarity, tileable, seed)
    return (noise_map - np.min(noise_map)) / (np.max(noise_map) - np.min(noise_map))


def generate_texture(shape=1024, res=8):
    texture = np.zeros((shape, shape, 3), dtype=np.uint8)
    noise_map = generate_noise(shape, res)

    for i in range(shape):
        for j in range(shape):
            texture[i, j] = biome_color(noise_map[i, j])
    return texture
