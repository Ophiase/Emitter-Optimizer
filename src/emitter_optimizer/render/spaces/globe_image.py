import itertools
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw

from emitter_optimizer.render.map import PLASMA

BACKGROUND = "#fbfaf6"
EMITTER = "crimson"
EDGE = "#ffffff"
LAND_LIFT = 0.22
EDGE_STEPS = 32
SMOOTHING = 4


def _smooth(field: np.ndarray) -> np.ndarray:
    rows, columns = field.shape
    image = Image.fromarray(field.astype(np.float32), "F")
    larger = (columns * SMOOTHING, rows * SMOOTHING)
    return np.asarray(image.resize(larger, Image.Resampling.BICUBIC))


def _indices(
    shape: tuple[int, ...], lat: np.ndarray, lon: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Where each latitude and longitude falls in a north-first grid."""
    rows, columns = shape
    row = np.clip(((np.pi / 2 - lat) / np.pi * rows).astype(int), 0, rows - 1)
    column = ((lon + np.pi) / (2 * np.pi) * columns).astype(int) % columns
    return row, column


@dataclass(frozen=True, slots=True)
class GlobeImage:
    """An orthographic view of a latitude-longitude field, north first."""

    field: np.ndarray
    land: np.ndarray | None = None
    size: int = 420

    def draw(
        self,
        emitters: np.ndarray,
        longitude: float = 0.0,
        latitude: float = 20.0,
        edges: np.ndarray | None = None,
    ) -> Image.Image:
        """`emitters` are unit vectors; `edges` are `(edges, 2, 3)` end points."""
        east, north, centre = self._basis(longitude, latitude)
        image = Image.fromarray(self._pixels(east, north, centre), "RGB")
        draw = ImageDraw.Draw(image)
        if edges is not None:
            for first, second in edges:
                self._edge(draw, first, second, east, north, centre)
        radius = max(4, self.size // 60)
        for emitter in emitters:
            if emitter @ centre <= 0.0:
                continue
            x, y = self._to_pixel(emitter, east, north)
            box = (x - radius, y - radius, x + radius, y + radius)
            draw.ellipse(box, fill=EMITTER, outline="#ffffff", width=2)
        return image

    def _basis(
        self, longitude: float, latitude: float
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        lon, lat = np.radians(longitude), np.radians(latitude)
        centre = np.array([
            np.cos(lat) * np.cos(lon),
            np.cos(lat) * np.sin(lon),
            np.sin(lat),
        ])
        east = np.array([-np.sin(lon), np.cos(lon), 0.0])
        north = np.array([
            -np.sin(lat) * np.cos(lon),
            -np.sin(lat) * np.sin(lon),
            np.cos(lat),
        ])
        return east, north, centre

    def _pixels(
        self, east: np.ndarray, north: np.ndarray, centre: np.ndarray
    ) -> np.ndarray:
        axis = (np.arange(self.size) + 0.5) / self.size * 2.0 - 1.0
        x, y = np.meshgrid(axis, -axis)
        on_disc = x**2 + y**2 < 1.0
        z = np.sqrt(np.clip(1.0 - x**2 - y**2, 0.0, 1.0))
        world = x[..., None] * east + y[..., None] * north + z[..., None] * centre
        lat = np.arcsin(np.clip(world[..., 2], -1.0, 1.0))
        lon = np.arctan2(world[..., 1], world[..., 0])
        low, high = float(self.field.min()), float(self.field.max())
        share = _smooth((self.field - low) / (high - low or 1.0))
        colour = PLASMA[np.clip(share * 255.0, 0.0, 255.0).astype(np.uint8)][
            _indices(share.shape, lat, lon)
        ].astype(np.float64)
        if self.land is not None:
            lift = self.land[_indices(self.land.shape, lat, lon)][..., None] * LAND_LIFT
            colour = colour * (1.0 - lift) + 255.0 * lift
        colour = colour * (0.55 + 0.45 * z[..., None])
        background = np.array([0xFB, 0xFA, 0xF6], dtype=np.float64)
        return np.where(on_disc[..., None], colour, background).astype(np.uint8)

    def _to_pixel(
        self, point: np.ndarray, east: np.ndarray, north: np.ndarray
    ) -> tuple[float, float]:
        half = self.size / 2
        return half + half * float(point @ east), half - half * float(point @ north)

    def _edge(
        self,
        draw: ImageDraw.ImageDraw,
        first: np.ndarray,
        second: np.ndarray,
        east: np.ndarray,
        north: np.ndarray,
        centre: np.ndarray,
    ) -> None:
        shares = np.linspace(0.0, 1.0, EDGE_STEPS)[:, None]
        arc = first * (1.0 - shares) + second * shares
        arc = arc / np.linalg.norm(arc, axis=1, keepdims=True)
        for start, end in itertools.pairwise(arc):
            if start @ centre > 0.0 and end @ centre > 0.0:
                draw.line(
                    [
                        self._to_pixel(start, east, north),
                        self._to_pixel(end, east, north),
                    ],
                    fill=EDGE,
                    width=2,
                )
