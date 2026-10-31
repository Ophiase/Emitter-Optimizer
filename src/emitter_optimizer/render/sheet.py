import io
from collections.abc import Sequence
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

GAP = 16
LABEL_HEIGHT = 24
LABEL_COLOUR = "#1f2933"


@dataclass(frozen=True, slots=True)
class ContactSheet:
    """A transparent mosaic that keeps every tile's own aspect ratio."""

    columns: int = 3
    gap: int = GAP

    def png(self, tiles: Sequence[tuple[bytes, str]]) -> bytes:
        if not tiles:
            return b""
        images = [
            (Image.open(io.BytesIO(data)).convert("RGBA"), label)
            for data, label in tiles
        ]
        rows = [
            images[start : start + self.columns]
            for start in range(0, len(images), self.columns)
        ]
        width = max(image.width for image, _label in images)
        heights = [
            LABEL_HEIGHT + max(image.height for image, _label in row) for row in rows
        ]
        sheet_width = self.columns * width + (self.columns - 1) * self.gap
        sheet_height = sum(heights) + (len(rows) - 1) * self.gap
        sheet = Image.new("RGBA", (sheet_width, sheet_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.load_default(size=16)
        y = 0
        for row, row_height in zip(rows, heights, strict=True):
            row_width = len(row) * width + (len(row) - 1) * self.gap
            x = (sheet_width - row_width) // 2
            for image, label in row:
                draw.text((x, y), label, fill=LABEL_COLOUR, font=font)
                sheet.paste(image, (x, y + LABEL_HEIGHT))
                x += width + self.gap
            y += row_height + self.gap
        buffer = io.BytesIO()
        sheet.save(buffer, format="PNG")
        return buffer.getvalue()
