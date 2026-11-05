from dataclasses import dataclass

import jax
import jax.numpy as jnp
from jax import Array

from emitter_optimizer.kernel.coverage import Coverage
from emitter_optimizer.kernel.domain import Domain
from emitter_optimizer.kernel.laws import Physics
from emitter_optimizer.kernel.occlusion import HardOcclusion


@dataclass(frozen=True, slots=True)
class OnlineBound:
    """What no placement on the candidates can pass, seen from any placement.

    It holds when the gain is monotone and submodular: a law that sends no negative
    signal, and a sensor that is concave and non-decreasing. Off the candidates it
    says nothing. Without `candidates`, every point of the domain is one.
    """

    domain: Domain
    physics: Physics
    candidates: Array | None = None

    def of(self, positions: Array) -> float:
        candidates = self.domain.points if self.candidates is None else self.candidates
        sent = jax.jit(Coverage(self.domain, HardOcclusion(), self.physics).sent)
        received = jnp.sum(sent(jnp.asarray(positions)), axis=1)
        current = self._gains(received[:, None])[0]
        gains = self._gains(received[:, None] + sent(candidates)) - current
        best = jnp.sort(jnp.maximum(gains, 0.0))[-positions.shape[0] :]
        return float(current + jnp.sum(best))

    def _gains(self, received: Array) -> Array:
        scores = self.physics.sensor(received) * self.domain.measure[:, None]
        return jnp.mean(scores, axis=0)
