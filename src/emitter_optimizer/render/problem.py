import io
from dataclasses import dataclass

import numpy as np
from jax import Array
from PIL import Image

from emitter_optimizer.kernel import Coverage, Scene
from emitter_optimizer.render.map import MapImage

GAP = 16
BACKGROUND = "#fbfaf6"


@dataclass(frozen=True, slots=True)
class ProblemImage:
    """Demand on the left, score on the right, walls and emitters on both."""

    scene: Scene
    coverage: Coverage
    width: int = 600

    def png(self, positions: Array | np.ndarray) -> bytes:
        image = MapImage(self.scene, self.coverage, width=self.width)
        demand = Image.open(io.BytesIO(image.demand_png(positions)))
        score = Image.open(io.BytesIO(image.png(positions)))
        sheet = Image.new("RGB", (demand.width * 2 + GAP, demand.height), BACKGROUND)
        sheet.paste(demand, (0, 0))
        sheet.paste(score, (demand.width + GAP, 0))
        buffer = io.BytesIO()
        sheet.save(buffer, format="PNG")
        return buffer.getvalue()
