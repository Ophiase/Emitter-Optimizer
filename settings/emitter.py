import tensorflow as tf

# Be careful, tensorflow autograph, 
# don't work at run time.
# Use tf.cond instead of if/else statements, 
# tf.while_loop instead of loops. 

@tf.function
def eval(distance : tf.Variable) -> tf.Variable:
    '''
        This function represent how much signal you can receive
        from a single emitter,
        given your distance from the emitter
    '''
    
    signal_strength = tf.constant(5.0, dtype=tf.float32)
    
    return tf.exp(-(distance / signal_strength))
