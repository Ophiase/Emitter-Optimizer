from dataclasses import dataclass

import jax
from jax import Array

from emitter_optimizer.kernel.occlusion.base import Occlusion


@jax.tree_util.register_dataclass
@dataclass(frozen=True)
class SoftOcclusion(Occlusion):
    """A wall whose edge is blurred over about `1 / sharpness` world units."""

    sharpness: Array

    def side(self, signed_distance: Array) -> Array:
        return jax.nn.sigmoid(self.sharpness * signed_distance)
