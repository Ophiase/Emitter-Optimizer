# The objective

**[sketch]** Today `G` is a mean. A deployment rarely optimizes a mean.

## What exists

`G(U) = mean_x psi(r_U,C(x)) * mu(x)` ([gain](../engine/gain.md)). It rewards
the total service and nothing else: a cell served at 0.99 counts as much as
three cells at 0.33, and an uncovered neighbourhood disappears in the
average.

## Candidates

| Objective | Says | Use when |
| --- | --- | --- |
| Mean gain | total service | a first answer, a benchmark |
| Coverage | share of cells above a threshold | a service guarantee |
| Quantile | the worst decile still served | fairness |
| Max-min | the worst cell, raised | no one left out |
| Weighted sum | gain minus cost | a budget per emitter |

## [sketch] How it fits

An objective is a function of the per-cell values `psi(r(x)) * mu(x)`:

```text
mean      -> average
coverage  -> average of (value > threshold)
quantile  -> the q-th smallest value
max-min   -> the smallest value
```

All but coverage are differentiable almost everywhere; coverage needs a
smooth threshold (a sigmoid) or a two-stage approach: maximize a soft
coverage, then count exactly.

## [caution]

Changing the objective changes the landscape, not only the number. Every new
objective needs its own baseline run ([baselines](baselines.md)) and its own
figure, or the comparison is meaningless.
