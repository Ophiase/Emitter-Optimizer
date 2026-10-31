from jax import numpy as np

ACTIVATION_PENALTY = 0.5
SATURATION = 1.5
QUARTER_TURN = 3.141 / 2.0


def _score(signal: np.ndarray | float) -> np.ndarray:
    return (np.sin(signal * QUARTER_TURN) - ACTIVATION_PENALTY) / (
        1.0 - ACTIVATION_PENALTY
    )


def eval(signal: np.ndarray) -> np.ndarray:
    """Score of a sensor that receives the sum of its emitters' signals."""
    return np.where(signal > SATURATION, _score(SATURATION), _score(signal))
