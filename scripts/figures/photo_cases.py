from dataclasses import dataclass, field
from io import BytesIO

import jax
import jax.numpy as jnp
import numpy as np
from PIL import Image

from emitter_optimizer.kernel import (
    Coverage,
    Descender,
    DescentSettings,
    Greedy,
    HardOcclusion,
    Relocation,
    Step,
)
from emitter_optimizer.maps.cases import Situation
from emitter_optimizer.render import CurveImage, PhotoImage
from emitter_optimizer.service.paths import PROJECT_ROOT

FIGURES = PROJECT_ROOT / "docs" / "figures" / "cases"
STEPS = 300
EVERY = 6
POLISH_STEPS = 150
POLISH_EVERY = 30
POLISH_STEP = 0.003
FRAME_MILLISECONDS = 70
JUMP_MILLISECONDS = 420
HOLD_MILLISECONDS = 2400
COUNT_FACTOR = 2


@dataclass
class Track:
    """Every placement a search visited, and which of them it reached by a jump."""

    path: list[np.ndarray]
    jumps: set[int] = field(default_factory=set)

    def capture(self, step: Step) -> None:
        self.path.append(np.asarray(step.positions))

    def durations(self) -> list[int]:
        return [
            HOLD_MILLISECONDS
            if index == len(self.path) - 1
            else (JUMP_MILLISECONDS if index in self.jumps else FRAME_MILLISECONDS)
            for index in range(len(self.path))
        ]


def search(situation: Situation, seed: int = 0) -> Track:
    """A random start, the descent, the relocations, then a polish."""
    scene, physics, emitters = situation.scene, situation.physics, situation.emitters
    start = scene.sample(jax.random.key(seed), 1, emitters)
    track = Track([np.asarray(start[0])])
    descent = Descender(
        scene,
        physics,
        DescentSettings(emitters, STEPS, report_every=EVERY, seed=seed),
        on_step=track.capture,
        start=start,
    ).run()
    current = descent.positions
    track.path.append(np.asarray(current))
    for placed in Relocation(scene, physics).jumps(current):
        current = placed
        track.path.append(np.asarray(placed))
        track.jumps.add(len(track.path) - 1)
    polish = Descender(
        scene,
        physics,
        DescentSettings(
            emitters, POLISH_STEPS, step_size=POLISH_STEP, report_every=POLISH_EVERY
        ),
        on_step=track.capture,
        start=current[None],
    ).run()
    track.path.append(np.asarray(polish.positions))
    return track


def _laws(situation: Situation, final: np.ndarray) -> Image.Image:
    scene, physics = situation.scene, situation.physics
    diagonal = float(jnp.linalg.norm(scene.bounds))
    distance = np.linspace(0.0, diagonal, 400)
    signal = np.asarray(physics.emitter(jnp.asarray(distance)))
    below = np.flatnonzero(signal < 0.02 * signal.max())
    cut = int(below[0]) + 1 if below.size else distance.size
    coverage = Coverage(scene, HardOcclusion(), physics)
    received = np.asarray(jnp.sum(coverage.sent(jnp.asarray(final)), axis=1))
    served = np.asarray(scene.measure) > 0
    top = float(np.quantile(received[served], 0.99)) or 1.0
    level = np.linspace(0.0, top, 400)
    left = CurveImage(
        distance[:cut],
        signal[:cut],
        "Emitter law: the signal of one emitter",
        "distance (m)",
    ).draw()
    right = CurveImage(
        level,
        np.asarray(physics.sensor(jnp.asarray(level))),
        "Sensor law: the score of a place",
        "received signal, up to what the map reaches",
    ).draw()
    sheet = Image.new("RGB", (left.width + right.width, left.height))
    sheet.paste(left, (0, 0))
    sheet.paste(right, (left.width, 0))
    return sheet


def _count(situation: Situation) -> Image.Image:
    """Greedy adds in order, so its prefixes answer every smaller budget at once."""
    scene, physics, emitters = situation.scene, situation.physics, situation.emitters
    placed = Greedy(scene, physics).place(emitters * COUNT_FACTOR)
    sent = Coverage(scene, HardOcclusion(), physics).sent(placed)
    received = jnp.cumsum(sent, axis=1)
    gains = jnp.mean(physics.sensor(received) * scene.measure[:, None], axis=0)
    counts = np.arange(1, gains.size + 1)
    values = np.asarray(gains)
    return CurveImage(
        counts,
        values,
        "The gain as emitters are added",
        "emitters (greedy placement)",
        mark=(float(emitters), float(values[emitters - 1])),
        mark_label=f"{emitters} in this case",
        width=880,
        height=280,
    ).draw()


def render(situation: Situation) -> int:
    """Write the case's figures; return how many jumps its search made."""
    FIGURES.mkdir(parents=True, exist_ok=True)
    name = situation.name
    track = search(situation)
    photo = PhotoImage.of(
        situation.scene,
        situation.physics,
        situation.source,
        situation.folder / "attraction.png",
    )
    frames = [
        photo.frame(track.path[: index + 1], track.jumps)
        for index in range(len(track.path))
    ]
    buffer = BytesIO()
    frames[0].save(
        buffer,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=track.durations(),
        loop=0,
        quality=70,
        method=4,
    )
    (FIGURES / f"{name}.webp").write_bytes(buffer.getvalue())
    frames[-1].save(FIGURES / f"{name}.jpg", quality=86)
    _laws(situation, track.path[-1]).save(FIGURES / f"{name}_laws.png")
    _count(situation).save(FIGURES / f"{name}_count.png")
    return len(track.jumps)
