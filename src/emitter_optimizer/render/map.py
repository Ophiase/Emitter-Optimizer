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


@dataclass(frozen=True, slots=True)
class MapImage:
    """A PNG of the value map, the walls and the emitters, drawn locally."""

    scene: Scene
    coverage: Coverage
    size: tuple[int, int] = (900, 600)

    def png(
        self,
        positions: Array | np.ndarray,
        trajectories: Sequence[Array | np.ndarray] | None = None,
    ) -> bytes:
        point_array = np.asarray(positions)
        values = np.asarray(
            self.coverage.value_map(jnp.asarray(point_array)), dtype=np.float64
        )
        top = float(values.max()) if values.size else 0.0
        normalised = values / top if top > 0 else np.zeros_like(values)
        gray = Image.fromarray((normalised * 255.0).astype(np.uint8), mode="L")
        image = ImageOps.colorize(
            gray.resize(self.size, Image.Resampling.BILINEAR),
            black="#071018",
            white="#f2c14e",
        ).convert("RGB")
        draw = ImageDraw.Draw(image)
        scale = np.array([self.size[0], self.size[1]], dtype=np.float64) / np.asarray(
            self.scene.bounds
        )
        for wall in np.asarray(self.scene.walls):
            draw.line(
                [tuple(wall[0] * scale), tuple(wall[1] * scale)],
                fill="#151515",
                width=WALL_WIDTH,
            )
        for path in trajectories or ():
            points = np.asarray(path)[:, :2] * scale
            draw.line([tuple(point) for point in points], fill="#ffffff", width=2)
        for point in point_array[:, :2] * scale:
            x, y = point
            box = (
                x - EMITTER_RADIUS,
                y - EMITTER_RADIUS,
                x + EMITTER_RADIUS,
                y + EMITTER_RADIUS,
            )
            draw.ellipse(box, fill="#e63946")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
