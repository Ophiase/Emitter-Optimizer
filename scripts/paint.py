from collections.abc import Callable
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_fill_holes, distance_transform_edt, gaussian_filter
from skimage.morphology import disk, opening, remove_small_objects

from emitter_optimizer.service.paths import PROJECT_ROOT

CASES = PROJECT_ROOT / "resources" / "cases"
FIGURES = PROJECT_ROOT / "docs" / "figures"
WALL_PIXELS = 10
PREVIEW_WIDTH = 400

type Point = tuple[float, float]
type Layers = tuple[np.ndarray, np.ndarray]


class Canvas:
    """A source photograph and the two layers painted over it."""

    def __init__(self, path: Path) -> None:
        self.rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64) / 255
        self.height, self.width = self.rgb.shape[:2]
        self.red, self.green, self.blue = self.rgb.transpose(2, 0, 1)
        self.brightness = self.rgb.mean(axis=2)
        self.saturation = self.rgb.max(axis=2) - self.rgb.min(axis=2)

    def polygon(self, *points: Point) -> np.ndarray:
        image = Image.new("L", (self.width, self.height), 0)
        ImageDraw.Draw(image).polygon(self._pixels(points), fill=255)
        return np.asarray(image) > 0

    def line(self, *points: Point) -> np.ndarray:
        image = Image.new("L", (self.width, self.height), 0)
        ImageDraw.Draw(image).line(self._pixels(points), fill=255, width=WALL_PIXELS)
        return np.asarray(image) > 0

    def band(self, top: float, bottom: float) -> np.ndarray:
        return self.polygon((0, top), (1, top), (1, bottom), (0, bottom))

    def smooth(self, values: np.ndarray, sigma: float = 3.0) -> np.ndarray:
        return np.clip(gaussian_filter(values.astype(np.float64), sigma), 0.0, 1.0)

    def _pixels(self, points: tuple[Point, ...]) -> list[tuple[float, float]]:
        return [(x * self.width, y * self.height) for x, y in points]


def garden(canvas: Canvas) -> Layers:
    grey = (canvas.saturation < 0.1) & (canvas.brightness > 0.3)
    red_roof = canvas.red > canvas.green + 0.15
    rows = (
        canvas.band(0.06, 0.14)
        | canvas.band(0.36, 0.43)
        | canvas.band(0.59, 0.67)
        | canvas.band(0.86, 0.94)
    )
    sheds = remove_small_objects(
        opening(rows & (grey | red_roof), disk(4)), max_size=500
    )
    soil = (
        (canvas.red > canvas.green)
        & (canvas.brightness < 0.4)
        & (canvas.saturation < 0.25)
    )
    plants = (canvas.green > canvas.red + 0.03) & (canvas.green > canvas.blue)
    paths = (
        canvas.band(0.0, 0.04)
        | canvas.band(0.31, 0.345)
        | canvas.band(0.815, 0.85)
        | canvas.polygon((0.97, 0), (1, 0), (1, 1), (0.97, 1))
    )
    attraction = canvas.smooth(1.0 * soil + 0.5 * plants) * ~paths * ~sheds
    return attraction, sheds


def beach(canvas: Canvas) -> Layers:
    water = (canvas.blue > canvas.red + 0.15) & (canvas.green > canvas.red + 0.1)
    water = binary_fill_holes(remove_small_objects(water, max_size=20000))
    water |= canvas.band(0.6, 1.0)
    from_shore = distance_transform_edt(water) / canvas.height
    sand = ~water & (canvas.brightness > 0.7) & (canvas.saturation < 0.2)
    swimmers = np.where(water, np.exp(-from_shore / 0.12), 0.0)
    headland = canvas.polygon(
        (0.50, 0.0),
        (0.50, 0.29),
        (0.565, 0.29),
        (0.585, 0.31),
        (0.63, 0.31),
        (0.66, 0.25),
        (0.72, 0.21),
        (0.84, 0.21),
        (0.86, 0.29),
        (0.94, 0.30),
        (0.94, 0.20),
        (0.97, 0.0),
    )
    rocks = canvas.polygon((0.515, 0.465), (0.55, 0.465), (0.55, 0.52), (0.515, 0.52))
    reef = canvas.polygon((0.565, 0.455), (0.61, 0.455), (0.61, 0.51), (0.565, 0.51))
    walls = headland | rocks | reef
    attraction = canvas.smooth(np.maximum(swimmers, 0.3 * sand)) * ~walls
    return attraction, walls


def marina(canvas: Canvas) -> Layers:
    sea = canvas.polygon(
        (0, 0),
        (1, 0),
        (1, 0.36),
        (0.86, 0.36),
        (0.70, 0.31),
        (0.58, 0.31),
        (0.48, 0.18),
        (0.45, 0.15),
        (0.10, 0.19),
        (0, 0.19),
    )
    water = sea | ((canvas.blue > canvas.red + 0.08) & (canvas.brightness < 0.5))
    basin = canvas.polygon((0.03, 0.19), (0.40, 0.25), (0.40, 0.93), (0.03, 0.93))
    boats = basin & (canvas.brightness > 0.75) & (canvas.saturation < 0.15)
    roofs = (canvas.red > canvas.blue + 0.15) & (canvas.red > canvas.green)
    quay_front = canvas.polygon(
        (0.355, 0.47), (0.40, 0.47), (0.40, 0.79), (0.355, 0.79)
    )
    town_front = canvas.polygon((0.42, 0.18), (0.46, 0.18), (0.46, 0.47), (0.42, 0.47))
    walls = quay_front | town_front
    people = 0.3 * ~water + 0.5 * roofs + 1.0 * gaussian_filter(boats * 1.0, 6) * 4
    return canvas.smooth(people) * ~walls, walls


def harbor(canvas: Canvas) -> Layers:
    water = (canvas.green > canvas.red + 0.04) & (canvas.brightness < 0.5)
    basin = canvas.polygon((0.10, 0.20), (0.80, 0.20), (0.80, 0.93), (0.10, 0.93))
    pier = canvas.polygon((0.66, 0.60), (0.80, 0.60), (0.80, 0.73), (0.68, 0.73))
    breakwater = canvas.polygon((0, 0), (0.045, 0), (0.045, 1), (0, 1))
    town = canvas.polygon((0.84, 0), (1, 0), (1, 1), (0.84, 1))
    land = ~water & ~(basin & ~pier) & ~breakwater
    walls = canvas.line((0.80, 0.0), (0.83, 0.18), (0.84, 0.40), (0.845, 0.95))
    attraction = canvas.smooth(land * np.where(town, 0.25, 1.0)) * ~walls
    return attraction, walls


def ramparts(canvas: Canvas) -> Layers:
    town = canvas.polygon(
        (0.30, 0.0),
        (1.0, 0.0),
        (1.0, 0.68),
        (0.93, 0.715),
        (0.74, 0.745),
        (0.36, 0.735),
        (0.315, 0.505),
        (0.30, 0.50),
    )
    palace = canvas.polygon((0.14, 0.24), (0.30, 0.24), (0.30, 0.50), (0.14, 0.50))
    built = (canvas.brightness > 0.65) | (canvas.red > canvas.blue + 0.2)
    trees = (canvas.green > canvas.red) & (canvas.green > canvas.blue)
    homes = np.where(built, 1.0, np.where(trees, 0.2, 0.5))
    walls = (
        canvas.line((0.04, 0.50), (0.315, 0.505), (0.36, 0.735), (0.50, 0.745))
        | canvas.line((0.50, 0.745), (0.735, 0.745))
        | canvas.line((0.765, 0.74), (0.93, 0.715), (1.0, 0.68))
        | canvas.line((0.06, 0.58), (0.19, 0.63), (0.30, 0.63))
        | canvas.line(
            (0.14, 0.24), (0.30, 0.24), (0.30, 0.50), (0.14, 0.50), (0.14, 0.24)
        )
    )
    attraction = canvas.smooth(homes * town + 0.5 * palace) * ~walls
    return attraction, walls


PAINTERS: dict[str, Callable[[Canvas], Layers]] = {
    "garden": garden,
    "beach": beach,
    "marina": marina,
    "harbor": harbor,
    "ramparts": ramparts,
}


def _preview(canvas: Canvas, attraction: np.ndarray, walls: np.ndarray) -> Image.Image:
    grey = canvas.brightness[..., None] * 0.45
    tint = np.array([1.0, 0.85, 0.2])
    rgb = grey * (1 - attraction[..., None]) + tint * attraction[..., None]
    rgb[walls] = (0.9, 0.1, 0.2)
    image = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
    height = round(PREVIEW_WIDTH * canvas.height / canvas.width)
    return image.resize((PREVIEW_WIDTH, height), Image.Resampling.LANCZOS)


def main() -> None:
    for name, paint in PAINTERS.items():
        folder = CASES / name
        canvas = Canvas(folder / "source.jpg")
        attraction, walls = paint(canvas)
        Image.fromarray((attraction * 255).astype(np.uint8)).save(
            folder / "attraction.png"
        )
        Image.fromarray(np.where(walls, 0, 255).astype(np.uint8)).save(
            folder / "collision.png"
        )
        _preview(canvas, attraction, walls).save(FIGURES / f"layers_{name}.jpg")


if __name__ == "__main__":
    main()
