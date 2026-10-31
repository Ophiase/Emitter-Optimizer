from dataclasses import dataclass

import jax
from jax import Array

from emitter_optimizer.kernel.occlusion.base import Occlusion


@jax.tree_util.register_dataclass
@dataclass(frozen=True)
class HardOcclusion(Occlusion):
    def side(self, signed_distance: Array) -> Array:
        return (signed_distance > 0).astype(signed_distance.dtype)
