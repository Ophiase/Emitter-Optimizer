# Occlusion

**[defined]** A wall blocks the signal: the segment between an emitter and a
cell either crosses an obstacle segment or it does not.

## Today

The test is the classical orientation test on two segments: `[x, y]` crosses
`[a, b]` when `a` and `b` are on opposite sides of `[x, y]` and `x` and `y` are
on opposite sides of `[a, b]`. `pass_C` is `0` or `1`, and an emitter is
never pushed through a wall by the gradient, because the gradient vanishes on
the far side.

## [sketch] The smooth version

Replace the indicator by a smooth crossing count, with a temperature `T`:

$$
pass_C(x, y) \;\simeq\; \sigma\!\left(-\frac{crossing(x, y)}{T}\right),
$$

where $\sigma$ is the logistic sigmoid and $crossing$ is a signed distance to
the obstacle, positive when the segment crosses.

where `crossing` is a signed distance to the obstacle, positive when the
segment crosses. `T -> 0` recovers the exact test; a finite `T` lets the
gradient flow through the wall, so the descent can *go around* a corner
instead of stopping.

## [caution] Traps

- A temperature that is too large blurs the map and creates minima at the
  scale of `T`; the benchmark must show the gain and the time against `T`.
- The exact test must remain available, and be the default, so a result can
  always be reproduced without a smooth approximation.
- The crossing count must be differentiable in `y`, which means the obstacle
  is a distance field, not a list of segments only; the two representations
  must agree on a crossing ([map](map.md)).

## Done when

An emitter placed against a wall moves along it and around its end when the
temperature is lowered, and the exact run at `T = 0` is unchanged.
