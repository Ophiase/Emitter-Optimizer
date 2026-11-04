import io
from collections.abc import Sequence
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from emitter_optimizer.render.charts.method_row import MethodRow

BACKGROUND = "#fbfaf6"
INK = "#1f2933"
MUTED = "#6b7280"
GRID = "#e8e4da"
GREEDY = "#c8553d"
DESCENT = "#2a6db5"
ROW_HEIGHT = 58
TOP = 86
LEFT = 170
RIGHT_MARGIN = 96
GRID_STEP = 10.0
MARKER = 8
FONT = ImageFont.load_default(size=16)


@dataclass(frozen=True, slots=True)
class MethodImage:
    """One row per case: how far each method lands above a random placement."""

    rows: Sequence[MethodRow]
    width: int = 900

    def png(self) -> bytes:
        height = TOP + ROW_HEIGHT * len(self.rows) + 30
        image = Image.new("RGB", (self.width, height), BACKGROUND)
        draw = ImageDraw.Draw(image)
        self._frame(draw, height)
        for index, row in enumerate(self.rows):
            self._row(draw, row, TOP + ROW_HEIGHT * index + 24)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    @property
    def _ceiling(self) -> float:
        highest = max(row.above_random(row.descent) for row in self.rows)
        return GRID_STEP * (1 + highest // GRID_STEP)

    def _x(self, percent: float) -> float:
        span = self.width - LEFT - RIGHT_MARGIN
        return LEFT + span * max(percent, 0.0) / self._ceiling

    def _frame(self, draw: ImageDraw.ImageDraw, height: int) -> None:
        draw.text((24, 16), "Gain above a random placement", fill=INK, font=FONT)
        draw.ellipse((24, 44, 36, 56), fill=GREEDY)
        draw.text((42, 42), "greedy on the grid", fill=INK, font=FONT)
        draw.ellipse((210, 44, 222, 56), fill=DESCENT)
        draw.text((228, 42), "gradient descent", fill=INK, font=FONT)
        percent = 0.0
        while percent <= self._ceiling:
            x = self._x(percent)
            draw.line([(x, TOP), (x, height - 30)], fill=GRID, width=1)
            draw.text(
                (x, height - 16), f"+{percent:.0f}%", fill=MUTED, font=FONT, anchor="mm"
            )
            percent += GRID_STEP

    def _row(self, draw: ImageDraw.ImageDraw, row: MethodRow, y: float) -> None:
        draw.text((24, y), row.case, fill=INK, font=FONT, anchor="lm")
        greedy, descent = row.above_random(row.greedy), row.above_random(row.descent)
        draw.line([(self._x(greedy), y), (self._x(descent), y)], fill=GRID, width=2)
        for percent, colour in ((greedy, GREEDY), (descent, DESCENT)):
            x = self._x(percent)
            draw.ellipse(
                (x - MARKER, y - MARKER, x + MARKER, y + MARKER),
                fill=colour,
                outline=BACKGROUND,
                width=2,
            )
        draw.text(
            (self._x(max(greedy, descent)) + 16, y),
            f"+{descent:.1f}%",
            fill=INK,
            font=FONT,
            anchor="lm",
        )
