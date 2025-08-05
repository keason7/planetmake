"""Main script."""

from src.planet import Planet
from src.render import Render


def main():
    """Initialize, draw and animate a planet."""
    planet = Planet(1.0, 50, 50)
    render = Render(planet)

    render.run()


if __name__ == "__main__":
    main()
