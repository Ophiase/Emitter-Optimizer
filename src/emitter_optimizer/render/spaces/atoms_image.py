from collections.abc import Sequence
from dataclasses import dataclass
from itertools import product

import numpy as np
from PIL import Image, ImageDraw

BACKGROUND = "#fbfaf6"
BOND = "#8a8f98"
FRAME = "#c9c4b8"
OUTLINE = "#1f2933"
BOND_LENGTH = 1.6
COLOURS = {"C": "#3a3f47", "N": "#2a6db5", "O": "#c8553d", "H": "#f4f2ec"}
RADII = {"C": 0.36, "N": 0.34, "O": 0.33, "H": 0.2}


@dataclass(frozen=True, slots=True)
class AtomsImage:
    """A ball-and-stick view of a periodic cell, turned about its vertical axis."""

    elements: Sequence[str]
    positions: np.ndarray
    cell: tuple[float, float, float]
    size: int = 520
    tilt: float = 18.0

    def draw(self, turn: float) -> Image.Image:
        image = Image.new("RGB", (self.size, self.size), BACKGROUND)
        draw = ImageDraw.Draw(image)
        elements, points = self.elements, self._whole_molecules()
        self._cell_frame(draw, turn)
        view = self._view(points, turn)
        for first, second in self._bonds(points):
            start, end = self._pixel(view[first]), self._pixel(view[second])
            draw.line([start, end], fill=BOND, width=4)
        for index in np.argsort(view[:, 2]):
            x, y = self._pixel(view[index])
            radius = RADII[elements[index]] * self._zoom
            box = (x - radius, y - radius, x + radius, y + radius)
            draw.ellipse(box, fill=COLOURS[elements[index]], outline=OUTLINE, width=1)
        return image

    @property
    def _zoom(self) -> float:
        return 0.86 * self.size / float(np.linalg.norm(self.cell))

    def _whole_molecules(self) -> np.ndarray:
        """Follow the bonds across the cell's faces, so no molecule is cut."""
        size = np.array(self.cell)
        points = self.positions.copy()
        placed: set[int] = set()
        for seed in range(len(points)):
            if seed in placed:
                continue
            placed.add(seed)
            frontier = [seed]
            while frontier:
                current = frontier.pop()
                offsets = points - points[current]
                nearest = offsets - size * np.round(offsets / size)
                lengths = np.sqrt(np.sum(nearest**2, axis=1))
                for other in np.nonzero(lengths < BOND_LENGTH)[0]:
                    if int(other) not in placed:
                        points[other] = points[current] + nearest[other]
                        placed.add(int(other))
                        frontier.append(int(other))
        return points

    def _bonds(self, points: np.ndarray) -> list[tuple[int, int]]:
        offsets = points[:, None, :] - points[None, :, :]
        lengths = np.sqrt(np.sum(offsets**2, axis=-1))
        rows, columns = np.nonzero((lengths > 0.1) & (lengths < BOND_LENGTH))
        return [(int(a), int(b)) for a, b in zip(rows, columns, strict=True) if a < b]

    def _cell_frame(self, draw: ImageDraw.ImageDraw, turn: float) -> None:
        size = np.array(self.cell)
        corners = np.array(list(product((0.0, 1.0), repeat=3))) * size
        view = self._view(corners, turn)
        for first in range(8):
            for second in range(first + 1, 8):
                if np.count_nonzero(corners[first] != corners[second]) == 1:
                    draw.line(
                        [self._pixel(view[first]), self._pixel(view[second])],
                        fill=FRAME,
                        width=2,
                    )

    def _view(self, points: np.ndarray, turn: float) -> np.ndarray:
        centred = points - np.array(self.cell) / 2.0
        angle, tilt = np.radians(turn), np.radians(self.tilt)
        x = centred[:, 0] * np.cos(angle) + centred[:, 1] * np.sin(angle)
        depth = -centred[:, 0] * np.sin(angle) + centred[:, 1] * np.cos(angle)
        up = centred[:, 2] * np.cos(tilt) + depth * np.sin(tilt)
        towards = depth * np.cos(tilt) - centred[:, 2] * np.sin(tilt)
        return np.stack([x, up, -towards], axis=1)

    def _pixel(self, point: np.ndarray) -> tuple[float, float]:
        half = self.size / 2
        return half + point[0] * self._zoom, half - point[1] * self._zoom
