import random

import matplotlib.pyplot as plt
import numpy as np

from src.perlin import perlin_noise
from src.utils import hex2rgb

_biomes = {
    "deep_ocean": {"color": "#101924"},
    "ocean": {"color": "#324f72"},
    "ice_ocean": {"color": "#c8c8ff"},
    "ice": {"color": "#ffffff"},
    "desert": {"color": "#fdd964"},
    "forest": {"color": "#385339"},
    "mountain": {"color": "#726147"},
    "placeholder": {"color": "#000000"},
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


def generate_world(shape, alti_map, temp_map):
    texture = np.zeros((shape, shape, 3), dtype=np.uint8)

    msk_water = alti_map <= 0
    msk_land = alti_map > 0

    texture[msk_water] = hex2rgb(_biomes["ocean"]["color"])
    texture[msk_water & (alti_map < -2000)] = hex2rgb(_biomes["deep_ocean"]["color"])
    texture[msk_water & (alti_map > -1000) & (temp_map < 0)] = hex2rgb(_biomes["ice_ocean"]["color"])

    texture[msk_land] = hex2rgb(_biomes["forest"]["color"])

    texture[msk_land & (alti_map > 3000)] = hex2rgb(_biomes["mountain"]["color"])
    texture[msk_land & (alti_map > 5000)] = hex2rgb(_biomes["ice"]["color"])
    texture[msk_land & (temp_map < -10)] = hex2rgb(_biomes["ice"]["color"])

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

    texture = generate_world(shape, altitude_map, temperature_map)

    return texture
