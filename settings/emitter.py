from jax import numpy as np

SIGNAL_STRENGTH = 5.0


def eval(distance: np.ndarray) -> np.ndarray:
    """Signal received from one emitter at `distance`, in the map's unit."""
    return np.exp(-(distance / SIGNAL_STRENGTH))
