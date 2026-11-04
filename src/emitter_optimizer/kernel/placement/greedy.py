from dataclasses import dataclass

import jax
import jax.numpy as jnp
from jax import Array

from emitter_optimizer.kernel.domain import Scene
from emitter_optimizer.kernel.laws import Physics
from emitter_optimizer.kernel.occlusion import HardOcclusion

LENGTH_FLOOR = 1e-12


@dataclass(frozen=True, slots=True)
class Greedy:
    """Add emitters one by one, each on the cell centre that helps most."""

    scene: Scene
    physics: Physics

    def place(self, emitters: int) -> Array:
        signal = self._signal()
        received = jnp.zeros(self.scene.cells.shape[0])
        chosen = []
        for _ in range(emitters):
            scores = self.physics.sensor(received[:, None] + signal)
            best = int(jnp.argmax(self.scene.measure @ scores))
            chosen.append(best)
            received = received + signal[:, best]
        return self.scene.cells[jnp.array(chosen)]

    def _signal(self) -> Array:
        """`(cells, candidates)`: what each candidate would send to each cell."""
        candidates = self.scene.cells
        offsets = self.scene.cells[:, None, :] - candidates[None, :, :]
        distances = jnp.sqrt(jnp.sum(offsets**2, axis=-1) + LENGTH_FLOOR)
        visible = jax.jit(self.scene.visibility, static_argnums=0)(
            HardOcclusion(), candidates
        )
        return self.physics.emitter(distances) * visible
