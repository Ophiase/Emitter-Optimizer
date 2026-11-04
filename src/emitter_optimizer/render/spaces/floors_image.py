import io
from dataclasses import dataclass

import jax.numpy as jnp
import numpy as np
from jax import Array
from PIL import Image, ImageColor, ImageDraw, ImageFont

from emitter_optimizer.kernel import Coverage, Volume
from emitter_optimizer.render.map import EMITTER, EMITTER_RADIUS, PLASMA, WALL

GAP = 8
TITLE_HEIGHT = 24
BACKGROUND = "#ffffff"
TITLE = "#1a1a1a"
FAINT_EMITTER = (220, 20, 60, 90)
DOOR_SHARE = 0.5


@dataclass(frozen=True, slots=True)
class FloorsImage:
    """A PNG with one storey per panel, side by side: a slice at `eye_layer`.

    `eye_layer` counts the voxels above the floor of a storey. The colours share
    one scale; an emitter on another storey is drawn faint.
    """

    volume: Volume
    coverage: Coverage
    storeys: int
    eye_layer: int = 1
    panel_width: int = 360

    def png(self, positions: Array | np.ndarray) -> bytes:
        return self._page(
            np.asarray(self.coverage.value_map(jnp.asarray(positions))), positions
        )

    def demand_png(self, positions: Array | np.ndarray) -> bytes:
        return self._page(
            np.asarray(self.volume.measure).reshape(self.volume.grid), positions
        )

    @property
    def _panel_height(self) -> int:
        width, height = np.asarray(self.volume.lengths)[:2]
        return round(self.panel_width * float(height / width))

    def _page(self, values: np.ndarray, positions: Array | np.ndarray) -> bytes:
        page_width = self.storeys * (self.panel_width + GAP) - GAP
        page = Image.new(
            "RGB", (page_width, self._panel_height + TITLE_HEIGHT), BACKGROUND
        )
        draw = ImageDraw.Draw(page)
        heights = (
            np.asarray(positions)[:, 2] * self.storeys / float(self.volume.lengths[2])
        )
        on_storey = np.clip(heights.astype(int), 0, self.storeys - 1)
        high = max(float(values.max()), 1e-12)
        font = ImageFont.load_default(15)
        for storey in range(self.storeys):
            left = storey * (self.panel_width + GAP)
            present = int(np.sum(on_storey == storey))
            title = f"Storey {storey + 1}: {present} emitters"
            draw.text((left, 3), title, fill=TITLE, font=font)
            panel = self._panel(values, high, storey, positions, on_storey)
            page.paste(panel, (left, TITLE_HEIGHT))
        buffer = io.BytesIO()
        page.save(buffer, format="PNG")
        return buffer.getvalue()

    def _panel(
        self,
        values: np.ndarray,
        high: float,
        storey: int,
        positions: Array | np.ndarray,
        on_storey: np.ndarray,
    ) -> Image.Image:
        layer = storey * self.volume.grid[2] // self.storeys + self.eye_layer
        indices = np.clip(values[:, :, layer].T / high * 255.0, 0.0, 255.0).astype(
            np.uint8
        )
        rgb = self._with_walls(PLASMA[indices], layer)
        size = (self.panel_width, self._panel_height)
        panel = Image.fromarray(rgb, mode="RGB").resize(size, Image.Resampling.NEAREST)
        self._draw_emitters(panel, np.asarray(positions), on_storey == storey)
        return panel

    def _with_walls(self, rgb: np.ndarray, layer: int) -> np.ndarray:
        absorption = np.asarray(self.volume.absorption)[:, :, layer].T
        strongest = max(float(absorption.max()), 1e-12)
        opacity = np.clip(absorption / (DOOR_SHARE * strongest), 0.0, 1.0)[..., None]
        wall = np.array(ImageColor.getrgb(WALL), dtype=np.float64)
        return (rgb * (1.0 - opacity) + wall * opacity).astype(np.uint8)

    def _draw_emitters(
        self, panel: Image.Image, positions: np.ndarray, here: np.ndarray
    ) -> None:
        draw = ImageDraw.Draw(panel, "RGBA")
        scale = self.panel_width / float(self.volume.lengths[0])
        for faint in (True, False):
            for point in positions[here != faint][:, :2] * scale:
                x, y = point
                box = (
                    x - EMITTER_RADIUS,
                    y - EMITTER_RADIUS,
                    x + EMITTER_RADIUS,
                    y + EMITTER_RADIUS,
                )
                if faint:
                    draw.ellipse(box, fill=FAINT_EMITTER)
                else:
                    draw.ellipse(box, fill=EMITTER, outline="#ffffff", width=1)
