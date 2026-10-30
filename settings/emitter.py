import tensorflow as tf

SIGNAL_STRENGTH = 5.0


@tf.function
def eval(distance: tf.Tensor) -> tf.Tensor:
    """Signal received from one emitter at `distance`, in the map's unit."""
    return tf.exp(-(distance / SIGNAL_STRENGTH))
