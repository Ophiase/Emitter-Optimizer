from jax import numpy as np

TARGET = 0.15
SOFTNESS = 0.03


def eval(signal: np.ndarray) -> np.ndarray:
    """A quay is lit once it passes the target; more light adds nothing."""
    return 1.0 / (1.0 + np.exp(-(signal - TARGET) / SOFTNESS))
