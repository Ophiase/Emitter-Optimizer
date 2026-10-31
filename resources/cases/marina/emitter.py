from jax import numpy as np

NEAR_FIELD = 20.0


def eval(distance: np.ndarray) -> np.ndarray:
    """Wi-Fi power: an inverse square that never reaches zero, in metres."""
    return 1.0 / (1.0 + (distance / NEAR_FIELD) ** 2)
