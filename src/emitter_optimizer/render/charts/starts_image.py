import io
from collections.abc import Sequence
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from emitter_optimizer.render.charts.method_row import MethodRow

BACKGROUND = "#fbfaf6"
INK = "#1f2933"
MUTED = "#6b7280"
GRID = "#e8e4da"
FREE = "#2a6db5"
RELOCATED = "#c8553d"
ROW_HEIGHT = 66
TOP = 92
LEFT = 110
RIGHT_MARGIN = 44
LANE = 12
MARKER = 6
FONT = ImageFont.load_default(size=16)


@dataclass(frozen=True, slots=True)
class StartsImage:
    """Each start of each case, as a shortfall from the best gain known for it."""

    rows: Sequence[MethodRow]
    width: int = 900

    def png(self) -> bytes:
        height = TOP + ROW_HEIGHT * len(self.rows) + 34
        image = Image.new("RGB", (self.width, height), BACKGROUND)
        draw = ImageDraw.Draw(image)
        self._frame(draw, height)
        for index, row in enumerate(self.rows):
            self._row(draw, row, TOP + ROW_HEIGHT * index + ROW_HEIGHT / 2)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    @property
    def _floor(self) -> float:
        lowest = max(
            self._shortfall(row, gain) for row in self.rows for gain in row.free
        )
        return 2.0 * (1 + lowest // 2.0)

    def _shortfall(self, row: MethodRow, gain: float) -> float:
        best = max(*row.free, *row.relocated, row.greedy, row.descent)
        return 100.0 * (best - gain) / best

    def _x(self, shortfall: float) -> float:
        span = self.width - LEFT - RIGHT_MARGIN
        return self.width - RIGHT_MARGIN - span * shortfall / self._floor

    def _frame(self, draw: ImageDraw.ImageDraw, height: int) -> None:
        draw.text(
            (24, 16),
            "How far each start ends below the best known",
            fill=INK,
            font=FONT,
        )
        draw.ellipse((24, 48, 36, 60), fill=FREE)
        draw.text((42, 46), "descent alone", fill=INK, font=FONT)
        draw.rectangle((190, 48, 202, 60), fill=RELOCATED)
        draw.text((208, 46), "then relocation and polish", fill=INK, font=FONT)
        tick = 0.0
        while tick <= self._floor:
            x = self._x(tick)
            draw.line([(x, TOP), (x, height - 30)], fill=GRID)
            draw.text(
                (x, height - 14), f"-{tick:.0f}%", fill=MUTED, font=FONT, anchor="mm"
            )
            tick += 2.0

    def _row(self, draw: ImageDraw.ImageDraw, row: MethodRow, y: float) -> None:
        draw.text((24, y), row.case, fill=INK, font=FONT, anchor="lm")
        for gain in row.free:
            x, lane = self._x(self._shortfall(row, gain)), y - LANE
            draw.ellipse(
                (x - MARKER, lane - MARKER, x + MARKER, lane + MARKER),
                fill=FREE,
                outline=BACKGROUND,
                width=2,
            )
        for gain in row.relocated:
            x, lane = self._x(self._shortfall(row, gain)), y + LANE
            draw.rectangle(
                (x - MARKER, lane - MARKER, x + MARKER, lane + MARKER),
                fill=RELOCATED,
                outline=BACKGROUND,
                width=2,
            )
