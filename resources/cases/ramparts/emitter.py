from jax import numpy as np

REFERENCE = 10.0
ABSORPTION = 300.0


def eval(distance: np.ndarray) -> np.ndarray:
    """Sound intensity of a siren: spherical spreading and air absorption."""
    return np.exp(-distance / ABSORPTION) / (1.0 + (distance / REFERENCE) ** 2)
