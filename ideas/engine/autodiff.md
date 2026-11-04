# Autodiff [decided]

JAX is the engine. A law is a `jax.numpy` function of one array; the gain is a
pure function of the positions, and `jax.value_and_grad` gives its gradient
exactly, once, with no finite difference and no analytic formula to maintain.

- The descent compiles one step with `jax.jit`, runs it with `lax.scan`, and
  vectorises the starts with `vmap`.
- `optax` supplies Adam, AdamW, Nadam, Lion and Nesterov SGD; each has a stable
  name, and the benchmark has one row per name.
- A law that `jax.grad` cannot trace is refused by the loader, with the file
  named in the message. There is no fallback: a silent finite difference hides
  the defect.
