from dataclasses import dataclass

import jax.numpy as jnp

from emitter_optimizer.kernel import Extent, GridShape, Scene
from emitter_optimizer.maps import Density, Walls


@dataclass(frozen=True, slots=True)
class Situation:
    name: str
    description: str
    density: Density | None
    walls: Walls | None
    extent: Extent
    grid: GridShape

    @property
    def scene(self) -> Scene:
        return Scene.of(
            self.extent,
            self.grid,
            None if self.density is None else jnp.asarray(self.density.values),
            None
            if self.walls is None
            else jnp.asarray(self.walls.to_world(self.extent)),
        )
