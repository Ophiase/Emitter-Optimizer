import tensorflow as tf

# Be careful, tensorflow autograph
# doesn't work at run time.
# Use tf.cond instead of if/else statements, 
# tf.while_loop instead of loops.

@tf.function
def eval(signal : tf.Variable) -> tf.Variable :
    '''
        This function represents, how your sensor process
        the sum of signals he received.
        It's similar to an activation function.
    '''

    activation_penalty = tf.constant(0.5, dtype=tf.float32)
    
    return tf.cond( signal > 1.5,
        lambda: (tf.sin(1.5 * 3.141 / 2.0) - activation_penalty)/(1.0-activation_penalty),
        lambda: (tf.sin(signal * 3.141 / 2.0) - activation_penalty)/(1.0-activation_penalty)
        )
