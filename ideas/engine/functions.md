# The two user laws [decided]

The physics is the user's: `emitter` maps a distance to a signal, `sensor` a
received sum to a score. Both are `jax.numpy` functions of one array.

```python
def eval(value: jnp.ndarray) -> jnp.ndarray: ...
```

- One array in, one array out, same shape, elementwise, pure.
- No `derivative`: JAX differentiates the law itself.
- No global state, no randomness, no printing, no `numpy` call on a traced
  value.

The loader checks that `jax.grad` traces what it reads and refuses a law that
it cannot, naming the file. It caches `Physics` by file content so `jit` does
not recompile for the same law.

`settings/emitter.py` and `settings/sensor.py` are the defaults; the window and
the command line edit them. The 2.x loader with its finite-difference fallback
is gone with `engine/`.
