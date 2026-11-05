from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw

from emitter_optimizer.kernel.placement.exact import (
    CoverProgram,
    ExactPlacement,
    Instance,
)

PANEL = 620
MARGIN = 20
SCALE = 2
BACKGROUND = (250, 250, 248)
COVERED = (46, 125, 50)
MISSED = (200, 80, 60)
WALL = (20, 20, 20)
EMITTER = (42, 109, 181)
DOT = 3


@dataclass(frozen=True, slots=True)
class ComparisonFigure:
    """One instance, solved on its demand points and solved to its proved optimum."""

    instance: Instance

    def image(self) -> Image.Image:
        sites = self.instance.points
        coverage = self.instance.covers(sites)
        kept = CoverProgram.maximal_rows(coverage)
        program = CoverProgram(
            coverage[kept], self.instance.weights, self.instance.emitters
        )
        restricted = sites[kept[list(program.solve().chosen)]]
        proved = ExactPlacement(self.instance).solve().positions
        canvas = Image.new(
            "RGB", (2 * PANEL + 3 * MARGIN, PANEL + 2 * MARGIN), BACKGROUND
        )
        canvas.paste(self._panel(restricted), (MARGIN, MARGIN))
        canvas.paste(self._panel(proved), (2 * MARGIN + PANEL, MARGIN))
        return canvas

    def _panel(self, positions: np.ndarray) -> Image.Image:
        size = PANEL * SCALE
        image = Image.new("RGB", (size, size), "white")
        draw = ImageDraw.Draw(image)
        ratio = size / self.instance.width
        reached = self.instance.covers(positions).any(axis=0)
        for point, covered in zip(self.instance.points * ratio, reached, strict=True):
            box = (*(point - DOT * SCALE), *(point + DOT * SCALE))
            draw.ellipse(box, fill=COVERED if covered else MISSED)
        for wall in self.instance.walls * ratio:
            draw.line(wall.reshape(-1).tolist(), fill=WALL, width=3 * SCALE)
        for position in positions * ratio:
            reach = self.instance.radius * ratio
            box = (*(position - reach), *(position + reach))
            draw.ellipse(box, outline=EMITTER, width=SCALE)
            spot = (*(position - 4 * DOT), *(position + 4 * DOT))
            draw.ellipse(spot, fill=EMITTER)
        return image.resize((PANEL, PANEL), Image.Resampling.LANCZOS)
