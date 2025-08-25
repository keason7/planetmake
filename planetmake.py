"""Main script."""

from src.planet import Planet
from src.render import Window
from src.texture import generate_texture


def planetmake():
    """Initialize, draw and animate a planet."""
    texture = generate_texture(shape=1024)

    window = Window(path_backgound="./assets/background.png")
    planet = Planet(1.0, texture)

    window.render(planet)


if __name__ == "__main__":
    planetmake()
