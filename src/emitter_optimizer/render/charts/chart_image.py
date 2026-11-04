import io
from collections.abc import Sequence
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

BACKGROUND = "#fbfaf6"
INK = "#1f2933"
MUTED = "#6b7280"
GRID = "#e8e4da"
AXIS = "#9aa3ad"
LINE = "#2f5d8a"
FILL = "#e8f0f7"


@dataclass(frozen=True, slots=True)
class ChartImage:
    history: Sequence[float]
    size: tuple[int, int] = (900, 340)

    def png(self) -> bytes:
        width, height = self.size
        image = Image.new("RGB", self.size, BACKGROUND)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default(size=16)
        left, top = 78, 56
        right, bottom = width - 32, height - 52
        plot_width, plot_height = right - left, bottom - top
        draw.text((left, 18), "Gain, iteration after iteration", fill=INK, font=font)
        draw.text((left, 31), "gain", fill=MUTED, font=font)
        if self.history:
            low = min(self.history)
            high = max(self.history)
            span = high - low or 1.0
            for index in range(5):
                y = top + plot_height * index / 4
                draw.line([(left, y), (right, y)], fill=GRID, width=1)
                value = high - span * index / 4
                draw.text(
                    (left - 8, y),
                    f"{value:.2f}",
                    fill=MUTED,
                    font=font,
                    anchor="rm",
                )
            draw.line([(left, top), (left, bottom)], fill=AXIS, width=1)
            draw.line([(left, bottom), (right, bottom)], fill=AXIS, width=1)
            step = plot_width / max(1, len(self.history) - 1)
            points = [
                (
                    left + index * step,
                    bottom - (value - low) / span * plot_height,
                )
                for index, value in enumerate(self.history)
            ]
            draw.polygon([*points, (right, bottom), (left, bottom)], fill=FILL)
            draw.line(points, fill=LINE, width=3)
            draw.text(
                (left + plot_width / 2, height - 30),
                "iteration",
                fill=MUTED,
                font=font,
                anchor="mm",
            )
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
