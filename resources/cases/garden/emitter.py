from jax import numpy as np

THROW = 6.0


def eval(distance: np.ndarray) -> np.ndarray:
    """Water from one sprinkler: none past its throw, in metres."""
    return np.clip(1.0 - (distance / THROW) ** 2, 0.0, None) ** 2
