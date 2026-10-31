# The language [decided]

**JAX is the engine; Python is the host.** The gradient, the step and the
multi-start loop are compiled by JAX; the laws are `jax.numpy`; `optax`
supplies the optimizers. Python keeps the faces (CLI, service, window) and the
orchestration.

A Rust kernel is not a speed question any more: the compiled JAX step already
beats the NumPy baseline by four to five times on CPU. Its only argument left
is a **geometry crate shared with the point-cloud project** — Kabsch, nearest
neighbours, point-cloud structures — and that is the author's decision
([open](../open.md)).

If it ever comes, it stays behind the same kernel API and the Python reference
stays as the test oracle. No rewrite for elegance.
