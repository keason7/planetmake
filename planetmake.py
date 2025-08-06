"""Main script."""

from src.planet import Planet
from src.render import Window
from src.texture import generate_texture


def main():
    """Initialize, draw and animate a planet."""
    window = Window()

    texture = generate_texture()
    planet = Planet(1.0, 50, 50, texture)

    window.render(planet)


if __name__ == "__main__":
    main()
