import tensorflow as tf

ACTIVATION_PENALTY = 0.5
SATURATION = 1.5
QUARTER_TURN = 3.141 / 2.0


def _score(signal: tf.Tensor) -> tf.Tensor:
    return (tf.sin(signal * QUARTER_TURN) - ACTIVATION_PENALTY) / (
        1.0 - ACTIVATION_PENALTY
    )


@tf.function
def eval(signal: tf.Tensor) -> tf.Tensor:
    """Score of a sensor that receives the sum of its emitters' signals."""
    return tf.cond(
        signal > SATURATION,
        lambda: _score(tf.constant(SATURATION)),
        lambda: _score(signal),
    )
