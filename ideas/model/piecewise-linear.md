# The piecewise-linear fast path

**[sketch]** From the original Future Development: approximate the gain by a
piecewise-linear function, so a large map becomes a fast integral.

## The idea

- `phi` and `psi` are approximated by piecewise-linear functions `l1`, `l2` on
  a relevant interval.
- `dist` is not linear, so it is approximated by Heron's iteration, which is
  a fixed number of arithmetic operations.
- The density is a piecewise-linear `l3`, integrated exactly over the cells.
- The gain becomes an integral of a piecewise-linear function: evaluable in
  parallel, with no transcendental call.

## Why it is worth keeping

It is the only idea in the original notes that changes the **complexity** of
the evaluation, not only the model. It is also testable: the approximation
has an error, and a benchmark can plot error against time for several
intervals.

## [caution]

- The approximation must not be used to claim a better gain: it approximates
  the same `G`, and the exact run is the truth.
- Heron's method has its own error, which compounds with the piecewise-linear
  error; both must appear in the table.
- The gradient of the approximation is piecewise constant, so the descent may
  stall; it needs its own stopping rule.

## Done when

A table gives, per map size, the exact time, the approximate time, and the
relative gain error, on the same seeds.
