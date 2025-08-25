"""Procedural generation texture of planet using Perlin Noise."""

import numpy as np
from PIL import Image

from src.perlin import perlin_noise_2d
from src.utils import get_latitude_grid, hex2rgba, random_seed

_biomes = {
    "ice_ocean": {
        "color": "#cacaec",
        "max_alti": 0,
        "min_alti": -1000,
        "max_temp": -5,
        "min_temp": None,
        "noise": 0.9,
    },
    "ocean": {
        "color": "#22344b",
        "max_alti": 0,
        "min_alti": -2000,
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
    "ice": {
        "color": "#ffffff",
        "max_alti": None,
        "min_alti": 0,
        "max_temp": -25,
        "min_temp": None,
        "noise": 0.3,
    },
    "pole_rock": {
        "color": "#726147",
        "max_alti": None,
        "min_alti": 0,
        "max_temp": -10,
        "min_temp": None,
        "noise": 0.9,
    },
    "mountain_ice": {
        "color": "#ffffff",
        "max_alti": None,
        "min_alti": 6000,
        "max_temp": None,
        "min_temp": None,
        "noise": 0.3,
    },
    "mountain": {
        "color": "#726147",
        "max_alti": None,
        "min_alti": 4000,
        "max_temp": None,
        "min_temp": None,
        "noise": 0.9,
    },
    "desert": {
        "color": "#e3c29c",
        "max_alti": 4000,
        "min_alti": 500,
        "max_temp": None,
        "min_temp": 29,
        "noise": 0.9,
    },
    "rock": {
        "color": "#d2a98e",
        "max_alti": 500,
        "min_alti": 0,
        "max_temp": None,
        "min_temp": 29,
        "noise": 0.9,
    },
    "plain": {
        "color": "#8e8b6b",
        "max_alti": 4000,
        "min_alti": 0,
        "max_temp": 29,
        "min_temp": 22,
        "noise": 0.9,
    },
    "dark_forest": {
        "color": "#2a3d2b",
        "max_alti": 4000,
        "min_alti": 2000,
        "max_temp": 22,
        "min_temp": None,
        "noise": 0.9,
    },
    "forest": {
        "color": "#385339",
        "max_alti": 2000,
        "min_alti": 0,
        "max_temp": 22,
        "min_temp": None,
        "noise": 0.9,
    },
}
_clouds = {
    "color": "#ffffff68",
    "noise": 0.9,
}

_earth = {
    "min_alti": -10000,
    "max_alti": 8000,
    "min_temp": -40,
    "max_temp": 35,
}


def generate_noise(shape, res, octaves=8, persistence=0.5, lacunarity=2.0, tileable=(True, True), seed=None):
    """Generate [0, 1] range perlin noise.

    Args:
        shape (int): Output array shape (shape, shape).
        res (int): Base resolution of noise (cells along each axis).
        octaves (int, optional): Number of perlin noises to sum. Defaults to 8.
        persistence (float, optional): Amplitude multiplier for each successive octave. Defaults to 0.5.
        lacunarity (float, optional): _descrFrequency multiplier for each successive octaveiption_. Defaults to 2.0.
        tileable (tuple, optional): Make noise tilable along an axis (avoid begin/end discontinuity).
            Defaults to (True, True).
        seed (int, optional): Random seed. Defaults to None.

    Returns:
        np.array: Perlin noise of shape (shape, shape) in [0, 1] range.
    """
    if seed is None:
        seed = random_seed()

    noise_map = perlin_noise_2d((shape, shape), (res, res), octaves, persistence, lacunarity, tileable, seed)
    return (noise_map - np.min(noise_map)) / (np.max(noise_map) - np.min(noise_map))


def generate_altitude_map(min_alt, max_alt, shape, res, seed=None):
    """Generate a procedural altitude map using perlin noise.

    Args:
        min_alt (int): Minimum altitude.
        max_alt (int): Maximum altitude.
        shape (int): Output array shape (shape, shape).
        res (int): Base resolution of noise (cells along each axis).
        seed (int, optional): Random seed. Defaults to None.

    Raises:
        ValueError: Min and/or max altitude value(s) are not valid.

    Returns:
        np.array: Altitude map.
    """
    if min_alt > 0 or max_alt < 0:
        raise ValueError(f"Min and/or max altitude value(s) are not valid, found [{min_alt}, {max_alt}]")

    noise_map = generate_noise(shape, res, seed=seed)
    altitude_map = np.zeros_like(noise_map)

    # scale land values from ]0.5, 1] to ]0, max_alt] and water values for [0, 0.5] to [min_alt, 0]
    msk_land = noise_map > 0.5
    msk_water = noise_map <= 0.5
    altitude_map[msk_land] = ((noise_map[msk_land] - 0.5) / 0.5) * max_alt
    altitude_map[msk_water] = ((noise_map[msk_water] - 0.5) / 0.5) * abs(min_alt)

    return altitude_map


def generate_temperature_map(min_temp, max_temp, altitude_map, shape, res, lapse_rate=9.2, seed=None):
    """Generate a procedural temperature map using perlin noise. Extrem high values are located on equator
    and low values on poles or in altitude with lapse_rate:
    https://en.wikipedia.org/wiki/Lapse_rate

    Args:
        min_temp (int): Minimum temperature.
        max_temp (int): Maximum temperature.
        altitude_map (np.array): Altitude map of shape (shape, shape).
        shape (int): Output array shape (shape, shape).
        res (int): Base resolution of noise (cells along each axis).
        lapse_rate (float, optional): Temperature fall rate with altitude (°C/km). Defaults to 9.2.
        seed (int, optional): Random seed. Defaults to None.

    Raises:
        ValueError: Minimum temperature cannot be higher or equal than maximum temperature.

    Returns:
        np.array: Temperature map.
    """
    if max_temp <= min_temp:
        raise ValueError("Minimum temperature cannot be higher or equal than maximum temperature.")

    noise_map = generate_noise(shape, res, seed=seed)

    # get latitude map: ranges from -90° (south pole) to +90° (north pole)
    latitude_map = get_latitude_grid(shape, shape)

    # compute latitude factor
    # equator (0°): cos(0) = 1
    # poles (90° or -90°): cos(90) or cos(-90) = 0
    latitude_factor = np.cos(np.radians(latitude_map))

    # interpolate between [min_temp, max_temp] depending on latitude factor (cold at poles, warm at equator)
    # add local noise variation (scaled between 10°C and -10°C)
    temperature_map = min_temp + latitude_factor * (max_temp - min_temp) + (noise_map - 0.5) * 20

    # decrease by lapse_rate °C per km (altitude) for land values (altitude > 0)
    lapse = (np.maximum(0, altitude_map) / 1000.0) * lapse_rate
    return temperature_map - lapse


def get_color(texture, msk, color, noise_map, noise=0.6):
    """Fetch and apply RGBA color to a set of pixels defined by a mask. The RGBA pixel color is modified
        pixel-wise based on a noise parameter.

    Args:
        texture (np.array): Texture array of shape (H, W, 4).
        msk (np.array): Selection mask.
        color (str): Hexadecimal RGBA color.
        noise_map (np.array): Perlin noise map for color shading.
        noise (float, optional): Noise intensity. Defaults to 0.6.

    Returns:
        np.array: Updated texture np.array of shape (H, W, 4).
    """
    # apply color on pixel selection
    texture[msk] = hex2rgba(color)

    # rescale noise values from [0, 1] → [1 - noise, 1 + noise]
    # ex: if noise=0.6, then range is [0.4, 1.6]
    # the higher the noise value is, the higher is the multiplier
    noise_map = 1 + (noise_map - 0.5) * 2 * noise

    # apply perlin blend on float64 and rescale as [0, 255] np.uint8
    texture = texture.astype(np.float64)
    texture[msk] = texture[msk] * noise_map[..., None][msk]
    return np.clip(texture, 0, 255).astype(np.uint8)


def alpha_composite(img_1, img_2):
    """Perform alpha compositing between two RGBA images.

    Args:
        img_1 (np.array): RGBA np.array of shape (H, W, 4).
        img_2 (np.array): RGBA np.array of shape (H, W, 4).

    Returns:
        np.array: Merged np.array of shape (H, W, 4).
    """
    # combine foreground image with transparency on background
    # new_px = fg_color * fg_alpha + bg_color * (1 - fg_alpha)
    # if fg_alpha = 1   => background is hidden
    # if fg_alpha = 0   => foreground is hidden
    # if fg_alpha = 0.5 => foreground and background are blended equally
    return np.array(
        Image.alpha_composite(
            Image.fromarray(img_1),
            Image.fromarray(img_2),
        )
    )


def generate_world(altitude_map, temperature_map, cloud_map, shape, res):
    """Generate world texture from perlin noises.

    Args:
        altitude_map (np.array): Atitude map from perlin noise.
        temperature_map (np.array): Temperature map from perlin noise.
        cloud_map (np.array): Cloud map from perlin noise.
        shape (int): Texture shape.
        res (int): Texture generation.

    Returns:
        np.array: World texture of shape (shape, shape, 4).
    """
    # create rgba world and cloud textures
    world_texture = np.zeros((shape, shape, 4), dtype=np.uint8)
    cloud_texture = np.zeros((shape, shape, 4), dtype=np.uint8)

    # perlin noise for colors variations
    color_shade_map = generate_noise(shape, res, persistence=0.8, seed=None)

    # mask of pixels available for selection
    msk_map = np.ones((shape, shape), dtype=np.bool)

    for biome_params in _biomes.values():
        # current biome mask
        msk = np.ones((shape, shape), dtype=np.bool)

        if biome_params["min_alti"] is not None:
            msk = msk & (biome_params["min_alti"] <= altitude_map)

        if biome_params["max_alti"] is not None:
            msk = msk & (altitude_map <= biome_params["max_alti"])

        if biome_params["min_temp"] is not None:
            msk = msk & (biome_params["min_temp"] <= temperature_map)

        if biome_params["max_temp"] is not None:
            msk = msk & (temperature_map <= biome_params["max_temp"])

        # apply current biome on pixels that have not been selected before
        msk = msk & msk_map
        msk_map[msk] = False

        world_texture = get_color(world_texture, msk, biome_params["color"], color_shade_map, biome_params["noise"])

    cloud_texture = get_color(cloud_texture, cloud_map > 0.55, _clouds["color"], color_shade_map, 0.6)

    # blend clouds and world textures
    return alpha_composite(world_texture, cloud_texture)


def generate_texture(shape=1024, res=8):
    """Generate 2D grid texture from procedural generation using perlin noise.

    Args:
        shape (int, optional): Texture shape. Defaults to 1024.
        res (int, optional): Texture generation. Defaults to 8.

    Returns:
        np.array: Generated texture.
    """
    altitude_map = generate_altitude_map(_earth["min_alti"], _earth["max_alti"], shape, res)
    temperature_map = generate_temperature_map(_earth["min_temp"], _earth["max_temp"], altitude_map, shape, res)
    cloud_map = generate_noise(shape, res, octaves=6, persistence=0.6)

    return generate_world(altitude_map, temperature_map, cloud_map, shape, res)
