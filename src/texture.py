"""Procedural generation texture of planet using Perlin Noise."""

import numpy as np

from src.perlin import perlin_noise_2d
from src.utils import get_latitude_grid, hex2rgb, random_seed

_biomes = {
    "ocean": {
        "color": "#22344B",
        "max_alti": 0,
        "min_alti": None,
        "max_temp": None,
        "min_temp": None,
        "noise": 0.9,
    },
    "deep_ocean": {
        "color": "#182636",
        "max_alti": -2000,
        "min_alti": None,
        "max_temp": None,
        "min_temp": None,
        "noise": 0.9,
    },
    "ice_ocean": {
        "color": "#b4b4ff",
        "max_alti": 0,
        "min_alti": -1000,
        "max_temp": 0,
        "min_temp": None,
        "noise": 0.6,
    },
    "forest": {
        "color": "#385339",
        "max_alti": None,
        "min_alti": 0,
        "max_temp": None,
        "min_temp": None,
        "noise": 0.7,
    },
    "mountain": {
        "color": "#726147",
        "max_alti": None,
        "min_alti": 3000,
        "max_temp": None,
        "min_temp": None,
        "noise": 0.6,
    },
    "mountain_ice": {
        "color": "#ffffff",
        "max_alti": None,
        "min_alti": 5000,
        "max_temp": None,
        "min_temp": None,
        "noise": 0.3,
    },
    "ice": {
        "color": "#ffffff",
        "max_alti": None,
        "min_alti": 0,
        "max_temp": -10,
        "min_temp": None,
        "noise": 0.3,
    },
}

_earth = {
    "min_alti": -10000,
    "max_alti": 8000,
    "min_temp": -40,
    "max_temp": 35,
}


def generate_noise(shape, res, octaves=6, persistence=0.55, lacunarity=2.0, tileable=(True, True), seed=None):
    if seed is None:
        seed = random_seed()

    noise_map = perlin_noise_2d((shape, shape), (res, res), octaves, persistence, lacunarity, tileable, seed)
    return (noise_map - np.min(noise_map)) / (np.max(noise_map) - np.min(noise_map))


def generate_altitude_map(min_alt, max_alt, shape, res, seed=None):
    noise_map = generate_noise(shape, res, seed=seed)

    msk_land = noise_map > 0.5
    msk_water = noise_map <= 0.5

    altitude_map = np.zeros_like(noise_map)
    altitude_map[msk_land] = ((noise_map[msk_land] - 0.5) / 0.5) * max_alt
    altitude_map[msk_water] = ((noise_map[msk_water] - 0.5) / 0.5) * abs(min_alt)

    return altitude_map


def generate_temperature_map(altitude_map, min_temp, max_temp, shape, res, seed=None):
    noise_map = generate_noise(shape, res, seed=seed)

    lat = get_latitude_grid(shape, shape)

    lat_factor = np.cos(np.radians(lat))
    temperature_map = min_temp + lat_factor * (max_temp - min_temp) + (noise_map - 0.5) * 20

    lapse = (np.maximum(0, altitude_map) / 1000.0) * 6.5
    temperature_map = temperature_map - lapse

    return temperature_map


def add_color(texture, msk, color, noise_map, noise=0.6):
    texture[msk] = hex2rgb(color)

    texture = texture.astype(np.float64)

    noise_map = 1 + (noise_map - 0.5) * 2 * noise

    noise_map_3d = noise_map[..., None]

    texture[msk] = texture[msk] * noise_map_3d[msk]

    return np.clip(texture, 0, 255).astype(np.uint8)


def generate_world(shape, res, alti_map, temp_map):
    texture = np.zeros((shape, shape, 3), dtype=np.uint8)

    color_shade_map = generate_noise(shape, res, persistence=0.7, seed=None)

    for biome_params in _biomes.values():
        msk = np.ones((shape, shape), dtype=np.bool)

        if biome_params["min_alti"] is not None:
            msk = msk & (alti_map > biome_params["min_alti"])

        if biome_params["max_alti"] is not None:
            msk = msk & (alti_map < biome_params["max_alti"])

        if biome_params["min_temp"] is not None:
            msk = msk & (temp_map > biome_params["min_temp"])

        if biome_params["max_temp"] is not None:
            msk = msk & (temp_map < biome_params["max_temp"])

        texture = add_color(texture, msk, biome_params["color"], color_shade_map, noise=biome_params["noise"])

    return texture


def generate_texture(shape=1024, res=8):
    altitude_map = generate_altitude_map(
        _earth["min_alti"],
        _earth["max_alti"],
        shape,
        res,
        seed=2079352251,
    )
    temperature_map = generate_temperature_map(
        altitude_map,
        _earth["min_temp"],
        _earth["max_temp"],
        shape,
        res,
        seed=2079352252,
    )

    texture = generate_world(shape, res, altitude_map, temperature_map)

    return texture
