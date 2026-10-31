import io
from collections.abc import Sequence
from dataclasses import dataclass

from PIL import Image, ImageDraw

MARGIN = 36
LINE = "#f2c14e"
BACKGROUND = "#0b0f14"


@dataclass(frozen=True, slots=True)
class ChartImage:
    history: Sequence[float]
    size: tuple[int, int] = (900, 320)

    def png(self) -> bytes:
        width, height = self.size
        image = Image.new("RGB", self.size, BACKGROUND)
        draw = ImageDraw.Draw(image)
        draw.rectangle(
            [MARGIN, MARGIN, width - MARGIN, height - MARGIN], outline="#2b3a4a"
        )
        if len(self.history) > 1:
            low = min(self.history)
            span = max(self.history) - low or 1.0
            step = (width - 2 * MARGIN) / (len(self.history) - 1)
            points = [
                (
                    MARGIN + index * step,
                    height - MARGIN - (value - low) / span * (height - 2 * MARGIN),
                )
                for index, value in enumerate(self.history)
            ]
            draw.line(points, fill=LINE, width=2)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
