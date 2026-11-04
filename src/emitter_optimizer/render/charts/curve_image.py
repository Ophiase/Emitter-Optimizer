from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw, ImageFont

BACKGROUND = "#fbfaf6"
INK = "#1f2933"
MUTED = "#6b7280"
GRID = "#e8e4da"
CURVE = "#2a6db5"
MARK = "#c8553d"
LEFT, RIGHT, TOP, BOTTOM = 62, 22, 46, 46
TICKS = 4
FONT = ImageFont.load_default(size=14)
TITLE = ImageFont.load_default(size=16)


@dataclass(frozen=True)
class CurveImage:
    """One curve, its title, and optionally the point the case actually uses."""

    x: np.ndarray
    y: np.ndarray
    title: str
    x_label: str
    mark: tuple[float, float] | None = None
    mark_label: str = ""
    width: int = 440
    height: int = 300

    def draw(self) -> Image.Image:
        image = Image.new("RGB", (self.width, self.height), BACKGROUND)
        draw = ImageDraw.Draw(image)
        draw.text((14, 12), self.title, fill=INK, font=TITLE)
        self._axes(draw)
        points = [
            self._pixel(float(x), float(y))
            for x, y in zip(self.x, self.y, strict=False)
        ]
        draw.line(points, fill=CURVE, width=2, joint="curve")
        if self.mark is not None:
            self._marker(draw, *self.mark)
        return image

    @property
    def _low(self) -> float:
        return min(0.0, float(self.y.min()))

    @property
    def _high(self) -> float:
        return float(self.y.max()) or 1.0

    @property
    def _x_ticks(self) -> np.ndarray:
        ticks = np.linspace(float(self.x.min()), float(self.x.max()), TICKS + 1)
        if np.issubdtype(self.x.dtype, np.integer):
            return np.unique(np.round(ticks))
        return ticks

    def _pixel(self, x: float, y: float) -> tuple[float, float]:
        first, last = float(self.x.min()), float(self.x.max())
        across = (x - first) / ((last - first) or 1.0)
        up = (y - self._low) / ((self._high - self._low) or 1.0)
        return (
            LEFT + across * (self.width - LEFT - RIGHT),
            self.height - BOTTOM - up * (self.height - TOP - BOTTOM),
        )

    def _axes(self, draw: ImageDraw.ImageDraw) -> None:
        for tick in np.linspace(self._low, self._high, TICKS + 1):
            _, y = self._pixel(float(self.x.min()), float(tick))
            draw.line([(LEFT, y), (self.width - RIGHT, y)], fill=GRID)
            draw.text((LEFT - 8, y), f"{tick:.3g}", fill=MUTED, font=FONT, anchor="rm")
        bottom = self.height - BOTTOM
        for tick in self._x_ticks:
            x, _ = self._pixel(float(tick), self._low)
            draw.text(
                (x, bottom + 14), f"{tick:.3g}", fill=MUTED, font=FONT, anchor="mm"
            )
        draw.text(
            ((LEFT + self.width - RIGHT) / 2, bottom + 34),
            self.x_label,
            fill=MUTED,
            font=FONT,
            anchor="mm",
        )

    def _marker(self, draw: ImageDraw.ImageDraw, x: float, y: float) -> None:
        px, py = self._pixel(x, y)
        draw.ellipse(
            (px - 6, py - 6, px + 6, py + 6), fill=MARK, outline=BACKGROUND, width=2
        )
        anchor = "rb" if px > self.width / 2 else "lb"
        offset = -10 if px > self.width / 2 else 10
        draw.text(
            (px + offset, py - 10), self.mark_label, fill=INK, font=FONT, anchor=anchor
        )
