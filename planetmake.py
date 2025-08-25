"""Main script."""

from src.planet import Planet
from src.render import Window
from src.texture import generate_texture


def planetmake():
    """Initialize, draw and animate a planet."""
    texture = generate_texture(shape=1024)

    planet = Planet(1.0, texture)

    window = Window(path_backgound="./assets/background.png")
    window.render(planet)


if __name__ == "__main__":
    planetmake()
