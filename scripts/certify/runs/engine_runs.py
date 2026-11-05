import time
from dataclasses import dataclass

import jax
import jax.numpy as jnp
import numpy as np
from jax import Array

from emitter_optimizer.kernel import (
    Descender,
    DescentResult,
    DescentSettings,
    Greedy,
    GridShape,
    Physics,
    Relocation,
    Scene,
)
from emitter_optimizer.kernel.placement.exact import Instance
from scripts.certify.runs.engine_scores import EngineScores

GRID_SIDE = 64
STARTS = 4
STEPS = 300
FREE_STEP = 0.01
POLISH_STEP = 0.003
REPORT_EVERY = 20
SOFTNESS_SHARE = 0.05


@dataclass(frozen=True, slots=True)
class EngineRuns:
    """The published search of `just bench`, on a reference instance.

    The sharp law steers the jumps; a gradient needs the blurred one, whose edge is
    a share of the radius. Every placement is scored by the instance, never by
    the law it was searched with.
    """

    instance: Instance
    softness_share: float = SOFTNESS_SHARE

    @property
    def scene(self) -> Scene:
        count = self.instance.points.shape[0]
        return Scene(
            points=jnp.asarray(self.instance.points, dtype=jnp.float32),
            measure=jnp.asarray(self.instance.weights / self.instance.weights.mean()),
            walls=jnp.asarray(self.instance.walls, dtype=jnp.float32),
            bounds=jnp.array([self.instance.width, self.instance.height]),
            grid=GridShape(1, count),
        )

    @property
    def sharp(self) -> Physics:
        radius = self.instance.radius
        return Physics(
            emitter=lambda distance: (distance <= radius).astype(distance.dtype),
            sensor=lambda signal: jnp.minimum(signal, 1.0),
        )

    @property
    def blurred(self) -> Physics:
        radius = self.instance.radius
        softness = radius * self.softness_share
        return Physics(
            emitter=lambda distance: jax.nn.sigmoid((radius - distance) / softness),
            sensor=lambda signal: jnp.minimum(signal, 1.0),
        )

    @property
    def grid(self) -> Array:
        axis = jnp.linspace(0.0, self.instance.width, GRID_SIDE)
        return jnp.stack(jnp.meshgrid(axis, axis), axis=-1).reshape(-1, 2)

    def run(self, seed: int = 0) -> EngineScores:
        started = time.perf_counter()
        greedy = Greedy(self.scene, self.sharp, self.grid).place(self.instance.emitters)
        free = self._free(seed)
        relocated = (self._jump(free.positions), self._jump(greedy))
        polished = tuple(self._polish(positions).positions for positions in relocated)
        return EngineScores(
            self._score(greedy),
            max(
                self._score(free.positions), self._score(self._polish(greedy).positions)
            ),
            max(self._score(positions) for positions in (*relocated, *polished)),
            time.perf_counter() - started,
        )

    def _free(self, seed: int) -> DescentResult:
        settings = DescentSettings(
            self.instance.emitters,
            STEPS,
            starts=STARTS,
            step_size=FREE_STEP,
            report_every=REPORT_EVERY,
            seed=seed,
        )
        return Descender(
            self.scene, self.blurred, settings, start=self._starts(seed)
        ).run()

    def _starts(self, seed: int) -> Array:
        weights = self.instance.weights / self.instance.weights.sum()
        chosen = np.random.default_rng(seed).choice(
            self.instance.points.shape[0],
            (STARTS, self.instance.emitters),
            p=weights,
        )
        return jnp.asarray(self.instance.points[chosen], dtype=jnp.float32)

    def _jump(self, positions: Array) -> Array:
        return Relocation(self.scene, self.sharp, self.grid).improve(positions)

    def _polish(self, positions: Array) -> DescentResult:
        settings = DescentSettings(
            self.instance.emitters,
            STEPS,
            step_size=POLISH_STEP,
            report_every=REPORT_EVERY,
        )
        return Descender(
            self.scene, self.blurred, settings, start=positions[None]
        ).run()

    def _score(self, positions: Array) -> int:
        return self.instance.covered_weight(np.asarray(positions, dtype=np.float64))
