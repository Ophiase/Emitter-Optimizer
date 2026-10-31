from typing import Protocol, runtime_checkable

from jax import Array


@runtime_checkable
class Law(Protocol):
    """A signal law: a distance or a received signal, cell by cell."""

    def __call__(self, values: Array, /) -> Array: ...
