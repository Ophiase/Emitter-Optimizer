from jax import numpy as np

POLE = 20.0


def eval(distance: np.ndarray) -> np.ndarray:
    """Illuminance on the ground from a lamp atop a pole, in metres."""
    return (1.0 + (distance / POLE) ** 2) ** -1.5
