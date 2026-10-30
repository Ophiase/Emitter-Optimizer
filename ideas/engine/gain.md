# The gain

**[defined]** The function the project maximizes, as it is implemented today.

## Notation

- `E`: the map, a rectangle of width `W` and height `H`; the grid has `R` rows
  and `C` columns.
- `mu`: a density over `E`, one non-negative weight per cell.
- `C`: a list of segments that block the signal.
- `U`: the positions of the emitters, `n` points of `E`.
- `phi: R+ -> R`: the emitter law, the signal received at a distance.
- `psi: R -> R`: the sensor law, the score of a received sum.
- `pass_C(x, y)`: `0` if the segment `[x, y]` crosses a segment of `C`, `1`
  otherwise ([occlusion](occlusion.md)).
- `dist(x, y) = ||x - y||_2` ([distance](distance.md)).

## The function

$$
r_{U, C}(x) = \sum_{y \in U} \varphi\bigl(dist(x, y)\bigr) \cdot pass_C(x, y),
\qquad
\mathcal G(U) = \frac{1}{R C} \sum_{x \in \text{grid}}
  \psi\bigl(r_{U, C}(x)\bigr) \, \mu(x).
$$

The mean over the cells is the integral against the uniform measure; with
`mu` normalized it is the expected value of `psi` under the density.

## What differentiability buys

`G` is differentiable in `U` wherever the laws are and wherever no emitter
crosses a segment: the sum is smooth, `dist` is smooth away from `x = y`, and
`pass_C` is locally constant.

$$
\frac{\partial \mathcal G}{\partial y}
= \frac{1}{R C} \sum_{x} \psi'\bigl(r(x)\bigr) \,
  \varphi'\bigl(dist(x, y)\bigr) \,
  \frac{y - x}{dist(x, y)} \,
  pass_C(x, y) \, \mu(x).
$$

That is the whole method: a gradient of a sum, evaluated on a grid, with a
mask. No framework is needed to obtain it, which is why NumPy replaces
TensorFlow ([optimizer](optimizer.md)).

## [caution] What the model assumes

- The signal adds linearly, with no interference.
- The obstacle test is binary, so an emitter on the wrong side of a wall has a
discontinuous gain.
- The density is piecewise constant on the grid: nearest cell, no
  interpolation.
- The map is a plane, not a surface ([distance](distance.md)).

Each assumption has a file in [../model/](../model/README.md) or here.
