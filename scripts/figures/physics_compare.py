from dataclasses import dataclass

import jax.numpy as jnp
import numpy as np
from jax import Array
from PIL import Image, ImageDraw, ImageFont

from emitter_optimizer.kernel import (
    Descender,
    DescentSettings,
    Physics,
    Relocation,
)
from emitter_optimizer.maps.cases import Situation
from emitter_optimizer.render import PhotoImage
from scripts.figures.photo_cases import FIGURES

STEPS = 300
POLISH_STEPS = 150
POLISH_STEP = 0.003
PANEL_WIDTH = 520
CAPTION = 62
BACKGROUND = "#fbfaf6"
INK = "#1f2933"
FONT = ImageFont.load_default(size=17)


def _lamp(distance: Array) -> Array:
    return (1.0 + (distance / 20.0) ** 2) ** -1.5


def _lit(signal: Array) -> Array:
    return 1.0 / (1.0 + jnp.exp(-(signal - 0.15) / 0.03))


def _wifi(distance: Array) -> Array:
    return 1.0 / (1.0 + (distance / 60.0) ** 2)


def _throughput(signal: Array) -> Array:
    return jnp.log1p(signal / 0.05) / jnp.log1p(1.0 / 0.05)


def _spray(distance: Array) -> Array:
    return jnp.clip(1.0 - (distance / 25.0) ** 2, 0.0, None) ** 2


def _dose(signal: Array) -> Array:
    return 1.0 - (1.0 - signal) ** 2


@dataclass(frozen=True, slots=True)
class Variant:
    title: str
    detail: str
    physics: Physics


VARIANTS = (
    Variant(
        "Lamps: lit or not",
        "a threshold fills the quays edge to edge",
        Physics(_lamp, _lit),
    ),
    Variant(
        "Wi-Fi: every bit counts",
        "diminishing returns pull toward the crowd",
        Physics(_wifi, _throughput),
    ),
    Variant(
        "Sprayers: one dose only",
        "a short reach and no overlap",
        Physics(_spray, _dose),
    ),
)


def _solve(situation: Situation, physics: Physics) -> np.ndarray:
    scene, emitters = situation.scene, situation.emitters
    descent = Descender(
        scene, physics, DescentSettings(emitters, STEPS, report_every=30)
    ).run()
    moved = Relocation(scene, physics).improve(descent.positions)
    polish = Descender(
        scene,
        physics,
        DescentSettings(emitters, POLISH_STEPS, step_size=POLISH_STEP, report_every=30),
        start=moved[None],
    ).run()
    return np.asarray(polish.positions)


def _panel(situation: Situation, variant: Variant) -> Image.Image:
    photo = PhotoImage.of(
        situation.scene,
        variant.physics,
        situation.source,
        situation.folder / "attraction.png",
        width=PANEL_WIDTH,
    )
    final = photo.frame([_solve(situation, variant.physics)])
    panel = Image.new("RGB", (final.width, final.height + CAPTION), BACKGROUND)
    panel.paste(final, (0, 0))
    draw = ImageDraw.Draw(panel)
    middle = final.width / 2
    draw.text(
        (middle, final.height + 19), variant.title, fill=INK, font=FONT, anchor="mm"
    )
    draw.text(
        (middle, final.height + 44), variant.detail, fill=INK, font=FONT, anchor="mm"
    )
    return panel


def render(situation: Situation) -> None:
    panels = [_panel(situation, variant) for variant in VARIANTS]
    sheet = Image.new(
        "RGB", (sum(panel.width for panel in panels), panels[0].height), BACKGROUND
    )
    for index, panel in enumerate(panels):
        sheet.paste(panel, (index * panel.width, 0))
    sheet.save(FIGURES / "same_map_three_laws.jpg", quality=86)
