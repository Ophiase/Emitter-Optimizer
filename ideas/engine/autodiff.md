# Autodiff: where it helps, where it does not

**[sketch]** The gradient of the gain in the emitter positions is analytic and
cheap: one pass over the cells, one sum, no graph. JAX is therefore not needed
for the core. It becomes useful at two precise seams, and the code should keep
those seams open rather than adopt a framework now.

## What the engine does today

- The built-in laws declare `derivative`; the exact gradient is used and tested
  against a central difference ([optimizer](optimizer.md)).
- A law without a derivative falls back to a central difference on that law
  ([functions](functions.md)). At fifteen emitters that is thirty evaluations
  of a one-dimensional function per iteration: measured in microseconds.

So the current cost is `O(P E)` for the gain and the gradient, with `P` cells
and `E` emitters. A framework would not change that order.

## Where JAX would earn its place

1. **A learned field** ([implicit energy](../model/implicit-energy.md)): the
   network's weights need a gradient that no closed form provides; `jax.grad`
   is the shortest path.
2. **A user law that is expensive and traceable**: a root, an integral, a
   small ODE inside `phi`. `jax.grad` differentiates it without rewriting the
   engine.
3. **A vectorized 3D gain** where `jax.jit` beats NumPy on the same sample
   count; this is a benchmark question, not an assumption.

## [caution] What a framework would cost now

- A second array library in the core, and a rule for which one a law may use.
- The pure-Python laws of `settings/` would not be traceable; the fallback to
  finite differences stays anyway.
- The published benchmark would have to show the gain per second, not the
  elegance of the graph.

## The seam to keep

A `Gradient` protocol next to `Law`, in the engine:

```python
class Gradient(Protocol):
    def __call__(self, field: Field, emitters: Positions) -> Positions: ...
```

`ExactGradient` is the current code; `FiniteDifferenceGradient` is the fallback;
`JaxGradient` is a later file behind an optional extra. The solver takes a
`Gradient`, so a backend is a line of configuration, not a rewrite.

## [question]

Does the implicit field arrive before the framework? It should: the field is a
model change, the framework is an implementation detail of it.
