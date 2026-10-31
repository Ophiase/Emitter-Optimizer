from jax import numpy as np

AUDIBLE_DECIBELS = -25.0
SOFTNESS_DECIBELS = 3.0


def eval(signal: np.ndarray) -> np.ndarray:
    """Heard once the level, in decibels, clears the street noise."""
    decibels = 10.0 * np.log10(signal + 1e-9)
    return 1.0 / (1.0 + np.exp(-(decibels - AUDIBLE_DECIBELS) / SOFTNESS_DECIBELS))
