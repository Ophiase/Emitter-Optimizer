from abc import ABC, abstractmethod

import optax


class Optimizer(ABC):
    """An optax transformation chosen by type, never by a free string."""

    @abstractmethod
    def to_optax(self, rate: float) -> optax.GradientTransformation:
        """Build the optax transformation at this learning rate."""
        raise NotImplementedError
