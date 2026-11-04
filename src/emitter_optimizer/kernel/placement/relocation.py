from collections.abc import Iterator
from dataclasses import dataclass

import jax
import jax.numpy as jnp
from jax import Array

from emitter_optimizer.kernel.coverage import Coverage
from emitter_optimizer.kernel.domain import Domain
from emitter_optimizer.kernel.laws import Physics
from emitter_optimizer.kernel.occlusion import HardOcclusion


@dataclass(frozen=True, slots=True)
class Relocation:
    """Move one emitter at a time to the candidate that helps most, while it helps.

    A gradient only feels the slope under an emitter, so it cannot leave a hill
    that a better one is hiding behind; this jump can, and never lowers the gain.
    Without `candidates`, every point of the domain is one.
    """

    domain: Domain
    physics: Physics
    candidates: Array | None = None
    tolerance: float = 1e-5
    passes: int = 40

    def improve(self, positions: Array) -> Array:
        current = jnp.asarray(positions)
        for placed in self.jumps(current):
            current = placed
        return current

    def jumps(self, positions: Array) -> Iterator[Array]:
        """Each placement after one more jump, the last being the local optimum."""
        candidates = self.domain.points if self.candidates is None else self.candidates
        sent = jax.jit(Coverage(self.domain, HardOcclusion(), self.physics).sent)
        offers = sent(candidates)
        current = jnp.asarray(positions)
        for _ in range(self.passes):
            jump = self._best_jump(sent(current), offers)
            if jump is None:
                return
            current = current.at[jump[0]].set(candidates[jump[1]])
            yield current

    def _best_jump(self, emitters: Array, offers: Array) -> tuple[int, int] | None:
        received = jnp.sum(emitters, axis=1)
        floor = float(self._scores(received[:, None])[0]) * (1.0 + self.tolerance)
        best, jump = floor, None
        for emitter in range(emitters.shape[1]):
            scores = self._scores((received - emitters[:, emitter])[:, None] + offers)
            candidate = int(jnp.argmax(scores))
            if float(scores[candidate]) > best:
                best, jump = float(scores[candidate]), (emitter, candidate)
        return jump

    def _scores(self, received: Array) -> Array:
        return jnp.mean(
            self.physics.sensor(received) * self.domain.measure[:, None], axis=0
        )
