from jax import numpy as np


def eval(signal: np.ndarray) -> np.ndarray:
    """Chance that at least one lifeguard gets there."""
    return 1.0 - np.exp(-signal)
