from dataclasses import dataclass

import jax
import jax.numpy as jnp
from jax import Array

from emitter_optimizer.kernel.domain import Domain
from emitter_optimizer.kernel.laws import Physics
from emitter_optimizer.kernel.occlusion import HardOcclusion


@dataclass(frozen=True, slots=True)
class Greedy:
    """Add emitters one by one, each on the candidate that helps most.

    Without `candidates`, every point of the domain is one.
    """

    domain: Domain
    physics: Physics
    candidates: Array | None = None

    def place(self, emitters: int) -> Array:
        candidates = self.domain.points if self.candidates is None else self.candidates
        signal = self._signal(candidates)
        received = jnp.zeros(self.domain.points.shape[0])
        chosen = []
        for _ in range(emitters):
            scores = self.physics.sensor(received[:, None] + signal)
            best = int(jnp.argmax(self.domain.measure @ scores))
            chosen.append(best)
            received = received + signal[:, best]
        return candidates[jnp.array(chosen)]

    def _signal(self, candidates: Array) -> Array:
        """`(points, candidates)`: what each candidate would send to each point."""
        visible = jax.jit(self.domain.visibility, static_argnums=0)(
            HardOcclusion(), candidates
        )
        return self.domain.signal(self.physics.emitter, candidates) * visible
