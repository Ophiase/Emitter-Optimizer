from abc import ABC, abstractmethod

from jax import Array

STATIC_METADATA = {"static": True}


class Occlusion(ABC):
    """How a point lies on the positive side of a wall, from 0 to 1."""

    @abstractmethod
    def side(self, signed_distance: Array) -> Array:
        """The share of a point on the positive side, from 0 to 1."""
        raise NotImplementedError
