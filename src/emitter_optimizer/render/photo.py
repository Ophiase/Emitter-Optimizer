from collections.abc import Collection, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Self

import jax
import jax.numpy as jnp
import numpy as np
from jax import Array
from PIL import Image, ImageDraw

from emitter_optimizer.kernel import (
    Coverage,
    Extent,
    GridShape,
    HardOcclusion,
    Law,
    Physics,
    Scene,
)

UNSERVED = np.array([0.16, 0.42, 1.0])
SERVED = np.array([1.0, 0.82, 0.12])
EMITTER = (220, 20, 60, 255)
RIM = (255, 255, 255, 255)
TRAIL = (255, 255, 255, 120)
JUMP = (255, 159, 28, 255)
PHOTO_COLOUR = 0.45
PHOTO_LIGHT = 0.62
OVERLAY = 0.62
SUPERSAMPLE = 2


@dataclass(frozen=True)
class PhotoImage:
    """The search on its photograph: blue demand is unserved, yellow is served."""

    backdrop: np.ndarray
    opacity: np.ndarray
    served: Law
    full_service: float
    world_to_pixel: np.ndarray

    @classmethod
    def of(
        cls,
        scene: Scene,
        physics: Physics,
        photograph: Path,
        attraction: Path,
        width: int = 720,
        refinement: int = 4,
    ) -> Self:
        photo = Image.open(photograph).convert("RGB")
        size = (width, round(width * photo.height / photo.width))
        pixels = np.asarray(photo.resize(size, Image.Resampling.LANCZOS), float) / 255.0
        grey = pixels.mean(axis=2, keepdims=True)
        demand = Image.open(attraction).convert("L")
        opacity = np.asarray(demand.resize(size, Image.Resampling.BILINEAR), float)
        grid = GridShape(scene.grid.rows * refinement, scene.grid.columns * refinement)
        width_m, height_m = (float(side) for side in scene.bounds)
        fine = Scene.of(Extent(width_m, height_m), grid, walls=scene.walls)
        coverage = Coverage(fine, HardOcclusion(), physics)

        def served(positions: Array) -> Array:
            received = jnp.sum(coverage.sent(positions), axis=1)
            return physics.sensor(received).reshape(grid.rows, grid.columns)

        return cls(
            backdrop=(PHOTO_COLOUR * pixels + (1.0 - PHOTO_COLOUR) * grey)
            * PHOTO_LIGHT,
            opacity=OVERLAY * (opacity / 255.0) ** 0.6,
            served=jax.jit(served),
            full_service=float(physics.sensor(jnp.ones(1))[0]),
            world_to_pixel=np.array(size) / np.asarray(scene.bounds),
        )

    def frame(
        self, path: Sequence[np.ndarray], jumps: Collection[int] = ()
    ) -> Image.Image:
        """The last placement of `path`, with the way there; `jumps` index arrivals."""
        height, width = self.opacity.shape
        image = self._map(path[-1], (width, height)).convert("RGBA")
        layer = Image.new(
            "RGBA", (width * SUPERSAMPLE, height * SUPERSAMPLE), (0, 0, 0, 0)
        )
        draw = ImageDraw.Draw(layer)
        self._trails(draw, path, jumps)
        self._emitters(draw, path[-1])
        layer = layer.resize((width, height), Image.Resampling.LANCZOS)
        return Image.alpha_composite(image, layer).convert("RGB")

    def _map(self, positions: np.ndarray, size: tuple[int, int]) -> Image.Image:
        values = np.asarray(self.served(jnp.asarray(positions)), float)
        share = np.clip(values / self.full_service, 0.0, 1.0)
        share = np.asarray(
            Image.fromarray((share * 255.0).astype(np.uint8)).resize(
                size, Image.Resampling.BICUBIC
            ),
            float,
        )
        tint = UNSERVED + (SERVED - UNSERVED) * (share[..., None] / 255.0) ** 0.8
        opacity = self.opacity[..., None]
        blended = self.backdrop * (1.0 - opacity) + tint * opacity
        return Image.fromarray((blended * 255.0).clip(0.0, 255.0).astype(np.uint8))

    def _pixel(self, point: np.ndarray) -> tuple[float, float]:
        x, y = point[:2] * self.world_to_pixel * SUPERSAMPLE
        return float(x), float(y)

    def _trails(
        self,
        draw: ImageDraw.ImageDraw,
        path: Sequence[np.ndarray],
        jumps: Collection[int],
    ) -> None:
        for index in range(1, len(path)):
            if index in jumps and index < len(path) - 1:
                continue
            moved = np.flatnonzero(np.any(path[index] != path[index - 1], axis=1))
            for emitter in moved:
                draw.line(
                    [
                        self._pixel(path[index - 1][emitter]),
                        self._pixel(path[index][emitter]),
                    ],
                    fill=JUMP if index in jumps else TRAIL,
                    width=(3 if index in jumps else 2) * SUPERSAMPLE // 2,
                )

    def _emitters(self, draw: ImageDraw.ImageDraw, positions: np.ndarray) -> None:
        radius = 5.5 * SUPERSAMPLE
        for point in positions:
            x, y = self._pixel(point)
            box = (x - radius, y - radius, x + radius, y + radius)
            draw.ellipse(box, fill=EMITTER, outline=RIM, width=SUPERSAMPLE)
