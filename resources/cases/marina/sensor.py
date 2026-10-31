from jax import numpy as np

NOISE = 0.05


def eval(signal: np.ndarray) -> np.ndarray:
    """Shannon throughput, in units of a link right under the antenna."""
    return np.log1p(signal / NOISE) / np.log1p(1.0 / NOISE)
