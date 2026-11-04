import jax.numpy as jnp
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from emitter_optimizer.kernel import Descender, DescentSettings, Physics, Sphere
from emitter_optimizer.render import GlobeImage
from emitter_optimizer.service.paths import PROJECT_ROOT

OUTPUT = PROJECT_ROOT / "docs" / "figures" / "sphere_polyhedra.png"
CONCENTRATION = 6.0
SOLIDS = (
    (4, "tetrahedron", 109.47),
    (6, "octahedron", 90.00),
    (12, "icosahedron", 63.43),
)
BACKGROUND = "#fbfaf6"
INK = "#1f2933"
SIZE = 380
CAPTION = 62
TOLERANCE = 1.08


PHYSICS = Physics(
    emitter=lambda angle: jnp.exp(CONCENTRATION * (jnp.cos(angle) - 1.0)),
    sensor=lambda signal: 1.0 - (1.0 - signal) ** 2,
)


def _edges(units: np.ndarray, smallest: float) -> np.ndarray:
    angles = np.degrees(np.arccos(np.clip(units @ units.T, -1.0, 1.0)))
    pairs = [
        (units[first], units[second])
        for first in range(len(units))
        for second in range(first + 1, len(units))
        if angles[first, second] < smallest * TOLERANCE
    ]
    return np.asarray(pairs)


def _panel(emitters: int, name: str, expected: float) -> Image.Image:
    sphere = Sphere.of(48, 96)
    settings = DescentSettings(
        emitters=emitters, steps=400, starts=6, step_size=0.02, report_every=50
    )
    result = Descender(sphere, PHYSICS, settings).run()
    units = np.asarray(sphere.project(result.positions))
    angles = np.degrees(np.arccos(np.clip(units @ units.T, -1.0, 1.0)))
    np.fill_diagonal(angles, 360.0)
    smallest = float(angles.min())
    signal = sphere.signal(PHYSICS.emitter, result.positions)
    field = np.asarray(PHYSICS.sensor(jnp.sum(signal, axis=1))).reshape(sphere.shape)
    globe = GlobeImage(field, size=SIZE).draw(
        units, longitude=25.0, latitude=25.0, edges=_edges(units, smallest)
    )
    panel = Image.new("RGB", (SIZE, SIZE + CAPTION), BACKGROUND)
    panel.paste(globe, (0, 0))
    draw = ImageDraw.Draw(panel)
    font = ImageFont.load_default(size=17)
    draw.text(
        (SIZE / 2, SIZE + 16),
        f"{emitters} emitters: {name}",
        fill=INK,
        font=font,
        anchor="mm",
    )
    draw.text(
        (SIZE / 2, SIZE + 42),
        f"smallest angle {smallest:.2f}° (exact {expected:.2f}°)",
        fill=INK,
        font=font,
        anchor="mm",
    )
    print(name, f"{smallest:.2f}", expected, flush=True)
    return panel


def main() -> None:
    panels = [_panel(*solid) for solid in SOLIDS]
    sheet = Image.new("RGB", (SIZE * len(panels), SIZE + CAPTION), BACKGROUND)
    for index, panel in enumerate(panels):
        sheet.paste(panel, (index * SIZE, 0))
    sheet.save(OUTPUT)


if __name__ == "__main__":
    main()
