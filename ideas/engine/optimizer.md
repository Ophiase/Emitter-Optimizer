# The optimizer

**[sketch]** Today a framework does the descent. Tomorrow the engine does it,
with the bounds the map implies.

## Today

`Solver.train` wraps the positions in a variable and asks Keras' Nadam to
minimize `-G`, for `n_iteration` steps, with a learning rate named `epsilon`.
An abort flag and an update callback make it usable from a window. It works;
it also drags TensorFlow and Keras into the core ([stack](../architecture/stack.md)).

## [sketch] The replacement

1. **Projected gradient**: `y <- clip(y - epsilon * dG/dy, 0, map_scale)`.
   The projection is the only constraint needed: an emitter stays on the map.
2. **Or L-BFGS-B** from `scipy.optimize.minimize` with the same bounds, when
   the gain is smooth enough (soft occlusion, or a density away from walls).
3. **Multi-start**: several initial placements from the seed, keep the best;
   the landscape of a mean gain is not convex.
4. **Stopping rule**: a relative gain below a tolerance, a maximum of
   iterations, or an abort.

## [question] What is `epsilon`?

Today it is Keras' learning rate, dimensionless. In a projected gradient it is
a step in map units. The interface must say which, or offer both
([open](../open.md)).

## Tests

- The gain never decreases on a benchmark situation.
- The exact gradient matches a central difference within `1e-4` relative.
- The same seed gives the same positions and the same history.
- An abort returns the positions reached so far, not an exception.
