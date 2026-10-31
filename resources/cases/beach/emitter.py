from jax import numpy as np

REACH = 35.0


def eval(distance: np.ndarray) -> np.ndarray:
    """Chance a lifeguard reaches a swimmer in time, in metres."""
    return np.exp(-((distance / REACH) ** 2))
