from dataclasses import dataclass

import jax
import optax
from jax import Array


@jax.tree_util.register_dataclass
@dataclass(frozen=True)
class Progress:
    positions: Array
    state: optax.OptState
