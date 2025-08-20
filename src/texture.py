import random

import matplotlib.pyplot as plt
import numpy as np

from src.perlin import perlin_noise
from src.utils import hex2rgb

_biomes = {
    "ocean": {
        "color": "#324f72",
        "max_alti": 0,
        "min_alti": 0,
        "max_temp": 0,
        "min_temp": 0,
    },
    "deep_ocean": {
        "color": "#101924",
        "max_alti": 0,
        "min_alti": 0,
        "max_temp": 0,
        "min_temp": 0,
    },
    "ice_ocean": {
        "color": "#c8c8ff",
        "max_alti": 0,
        "min_alti": 0,
        "max_temp": 0,
        "min_temp": 0,
    },
    "forest": {
        "color": "#385339",
        "max_alti": 0,
        "min_alti": 0,
        "max_temp": 0,
        "min_temp": 0,
    },
    "mountain": {
        "color": "#726147",
        "max_alti": 0,
        "min_alti": 0,
        "max_temp": 0,
        "min_temp": 0,
    },
    "ice": {
        "color": "#ffffff",
        "max_alti": 0,
        "min_alti": 0,
        "max_temp": 0,
        "min_temp": 0,
    },
}


def get_lat(shape):
    i = np.arange(shape)
    lat_1d = 90.0 - (i / (shape - 1)) * 180.0
    return np.tile(lat_1d[:, None], (1, shape))


def random_seed(seed_min=0, seed_max=2**32):
    return random.randint(int(seed_min), int(seed_max))


def generate_noise(shape, res, octaves=6, persistence=0.55, lacunarity=2.0, tileable=(True, True), seed=None):
    if seed is None:
        seed = random_seed()

    noise_map = perlin_noise((shape, shape), (res, res), octaves, persistence, lacunarity, tileable, seed)
    return (noise_map - np.min(noise_map)) / (np.max(noise_map) - np.min(noise_map))


def generate_altitude(min_alt, max_alt, shape, res, seed=None):
    noise_map = generate_noise(shape, res, seed=seed)

    msk_land = noise_map > 0.5
    msk_water = noise_map <= 0.5

    altitude_map = np.zeros_like(noise_map)
    altitude_map[msk_land] = ((noise_map[msk_land] - 0.5) / 0.5) * max_alt
    altitude_map[msk_water] = ((noise_map[msk_water] - 0.5) / 0.5) * abs(min_alt)

    return altitude_map


def generate_temperature(min_temp, max_temp, shape, res, seed=None):
    noise_map = generate_noise(shape, res, seed=seed)

    lat = get_lat(shape)

    lat_factor = np.cos(np.radians(lat))
    temperature_map = min_temp + lat_factor * (max_temp - min_temp) + (noise_map - 0.5) * 20

    return temperature_map


def add_color(texture, msk, color, shape, res, noise=0.6, seed=None):
    texture[msk] = hex2rgb(color)

    texture = texture.astype(np.float64)

    noise_map = generate_noise(shape, res, persistence=0.7, seed=seed)

    noise_map = 1 + (noise_map - 0.5) * 2 * noise

    noise_map_3d = noise_map[..., None]

    texture[msk] = texture[msk] * noise_map_3d[msk]

    return np.clip(texture, 0, 255).astype(np.uint8)


def generate_world(shape, res, alti_map, temp_map):
    texture = np.zeros((shape, shape, 3), dtype=np.uint8)

    msk_water = alti_map <= 0
    msk_land = alti_map > 0

    texture = add_color(texture, msk_water, _biomes["ocean"]["color"], shape, res, noise=0.9)

    texture = add_color(texture, msk_water & (alti_map < -2000), _biomes["deep_ocean"]["color"], shape, res, noise=0.9)

    texture = add_color(
        texture, msk_water & (alti_map > -1000) & (temp_map < 0), _biomes["ice_ocean"]["color"], shape, res
    )

    texture = add_color(texture, msk_land, _biomes["forest"]["color"], shape, res)

    texture = add_color(texture, msk_land & (alti_map > 3000), _biomes["mountain"]["color"], shape, res)

    texture = add_color(texture, msk_land & (alti_map > 5000), _biomes["ice"]["color"], shape, res, noise=0.3)

    texture = add_color(texture, msk_land & (temp_map < -10), _biomes["ice"]["color"], shape, res, noise=0.3)

    return texture


def plot_maps(temperature_map, altitude_map):
    _, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].imshow(temperature_map)
    axes[0].set_title("Temperature Map")
    axes[0].axis("off")

    axes[1].imshow(altitude_map)
    axes[1].set_title("Altitude Map")
    axes[1].axis("off")

    plt.show()


def generate_texture(shape=1024, res=8):

    altitude_map = generate_altitude(-12000, 8000, shape, res, 2079352251)
    temperature_map = generate_temperature(-40, 35, shape, res, 2079352252)

    lapse = (np.maximum(0, altitude_map) / 1000.0) * 6.5
    temperature_map = temperature_map - lapse

    # plot_maps(temperature_map, altitude_map)

    texture = generate_world(shape, res, altitude_map, temperature_map)

    return texture
