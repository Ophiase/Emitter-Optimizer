import io
from collections.abc import Sequence
from dataclasses import dataclass

import jax.numpy as jnp
import numpy as np
from jax import Array
from PIL import Image, ImageDraw, ImageOps

from emitter_optimizer.kernel import Coverage, Scene

EMITTER_RADIUS = 6
WALL_WIDTH = 2
LOW = "#fbfaf6"
HIGH = "#123b5c"
DEMAND_HIGH = "#c9c3b6"
WALL = "#1f2933"
EMITTER = "#c44536"
PATH = "#2f5d8a"


@dataclass(frozen=True, slots=True)
class MapImage:
    """A light PNG of the value map, the walls and the emitters."""

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
        return self._png(values, positions, trajectories, HIGH)

    def demand_png(self, positions: Array | np.ndarray) -> bytes:
        values = np.asarray(self.scene.measure, dtype=np.float64).reshape(
            self.scene.grid.rows, self.scene.grid.columns
        )
        return self._png(values, positions, None, DEMAND_HIGH)

    def _png(
        self,
        values: np.ndarray,
        positions: Array | np.ndarray,
        trajectories: Sequence[Array | np.ndarray] | None,
        high: str,
    ) -> bytes:
        top = float(values.max()) if values.size else 0.0
        normalised = values / top if top > 0 else np.zeros_like(values)
        height = max(
            1,
            round(
                self.width * float(self.scene.bounds[1]) / float(self.scene.bounds[0])
            ),
        )
        gray = Image.fromarray((normalised * 255.0).astype(np.uint8), mode="L")
        image = ImageOps.colorize(
            gray.resize((self.width, height), Image.Resampling.NEAREST),
            black=LOW,
            white=high,
        ).convert("RGB")
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
