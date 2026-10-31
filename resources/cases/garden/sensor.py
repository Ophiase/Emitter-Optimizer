from jax import numpy as np


def eval(signal: np.ndarray) -> np.ndarray:
    """A bed wants one dose of water; a second one drowns it."""
    return 1.0 - (1.0 - signal) ** 2
