import io
from collections.abc import Sequence
from dataclasses import dataclass

import jax.numpy as jnp
import numpy as np
from jax import Array
from PIL import Image, ImageColor, ImageDraw
from plotly.colors import sample_colorscale

from emitter_optimizer.kernel import Coverage, Scene

EMITTER_RADIUS = 6
WALL_WIDTH = 2
WALL = "#1a1a1a"
EMITTER = "crimson"
PATH = "white"


def _palette(name: str) -> np.ndarray:
    samples = sample_colorscale(name, np.linspace(0.0, 1.0, 256).tolist())
    return np.array([ImageColor.getrgb(sample) for sample in samples], dtype=np.uint8)


PLASMA = _palette("Plasma")
GREYS = _palette("Greys")


@dataclass(frozen=True, slots=True)
class MapImage:
    """A PNG of the value map, the walls and the emitters."""

    scene: Scene
    coverage: Coverage
    width: int = 900

    def png(
        self,
        positions: Array | np.ndarray,
        trajectories: Sequence[Array | np.ndarray] | None = None,
    ) -> bytes:
        values = np.asarray(
            self.coverage.value_map(jnp.asarray(np.asarray(positions))),
            dtype=np.float64,
        )
        return self._png(values, positions, trajectories, PLASMA)

    def demand_png(self, positions: Array | np.ndarray) -> bytes:
        values = np.asarray(self.scene.measure, dtype=np.float64).reshape(
            self.scene.grid.rows, self.scene.grid.columns
        )
        return self._png(values, positions, None, GREYS)

    def _png(
        self,
        values: np.ndarray,
        positions: Array | np.ndarray,
        trajectories: Sequence[Array | np.ndarray] | None,
        palette: np.ndarray,
    ) -> bytes:
        top = float(values.max()) if values.size else 0.0
        normalised = values / top if top > 0 else np.zeros_like(values)
        height = max(
            1,
            round(
                self.width * float(self.scene.bounds[1]) / float(self.scene.bounds[0])
            ),
        )
        indices = (normalised * 255.0).astype(np.uint8)
        image = Image.fromarray(palette[indices], mode="RGB").resize(
            (self.width, height), Image.Resampling.NEAREST
        )
        draw = ImageDraw.Draw(image)
        scale = np.array([self.width, height], dtype=np.float64) / np.asarray(
            self.scene.bounds
        )
        for wall in np.asarray(self.scene.walls):
            draw.line(
                [tuple(wall[0] * scale), tuple(wall[1] * scale)],
                fill=WALL,
                width=WALL_WIDTH,
            )
        for path in trajectories or ():
            points = np.asarray(path)[:, :2] * scale
            draw.line([tuple(point) for point in points], fill=PATH, width=3)
        for point in np.asarray(positions)[:, :2] * scale:
            x, y = point
            box = (
                x - EMITTER_RADIUS,
                y - EMITTER_RADIUS,
                x + EMITTER_RADIUS,
                y + EMITTER_RADIUS,
            )
            draw.ellipse(box, fill=EMITTER, outline="#ffffff", width=1)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
