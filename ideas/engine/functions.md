# The two user laws

**[defined]** The physics is the user's: `phi` says how much signal a sensor
receives at a distance, `psi` says what it scores. The engine only
optimizes.

## The contract

```python
def eval(value: FloatArray) -> FloatArray: ...
```

- One array in, one array out, same shape, elementwise.
- `phi` is defined on `[0, +inf)`, `psi` on the whole line.
- Both must be pure: no global state, no randomness, no printing.

An optional companion closes the loop:

```python
def derivative(value: FloatArray) -> FloatArray: ...
```

When `derivative` is present the engine uses the exact gradient
([optimizer](optimizer.md)); when it is absent, it uses central differences.

## Today

`settings/emitter.py` and `settings/sensor.py`, loaded by `exec` of their
source. It works and it lets a person edit them in the window.

## [caution] What changes

- `exec` is not a contract: no validation, no clear error, no isolation. The
  roadmap replaces it by a plugin module (`eval`, optional `derivative`) or a
  restricted expression language ([roadmap](../roadmap.md)).
- A law written with TensorFlow operations must be rewritten in NumPy;
  `tf.exp` becomes `np.exp`.
- Precision is `float64` in the engine; a law returning `float32` is cast
  once, with a test.
