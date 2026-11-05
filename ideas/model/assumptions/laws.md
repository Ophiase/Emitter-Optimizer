# The two laws: what their shape gives

**The shape of $\psi$ decides the guarantee; the shape of $\varphi$ decides what
a gradient can see.** Claims marked tested are in
`tests/kernel/test_law_classes.py`.

Write $a_y(x) = \varphi(d(x, y)) \, pass_C(x, y)$, the signal of one emitter.

## The master result

**[proved]** If $a_y \ge 0$, $\mu \ge 0$ and $\psi$ is concave, then
$\mathcal G$ is submodular: an emitter helps a large set no more than a small one.

- **Proof**: at each $x$, a concave function of a sum of non-negative terms has
  diminishing increments; integrating against $\mu \ge 0$ keeps them.
- **It never uses** the distance, the walls or the dimension. They only change the
  $a_y$, so the result holds on a sphere, in a building and on a calendar.
- **If $\psi$ is also non-decreasing**, the gain is monotone, and greedy reaches
  $1 - 1/e$ of the optimum among candidates (Nemhauser, Wolsey and Fisher, 1978).

## Classes of $\psi$

| Class | Constraint | Consequence | Status |
| --- | --- | --- | --- |
| Linear | $\psi(s) = s$ | Every emitter goes to the same best place | **[proved]** tested |
| Saturating | Concave, non-decreasing | $1 - 1/e$, and an online bound | **[proved]** tested |
| Dome | Concave, decreasing past a peak | Submodular, not monotone: one more emitter can hurt | **[proved]** tested |
| Quadratic | $\psi(s) = 2s - s^2$ | A field minus a pair energy | **[proved]** tested |
| Logarithm | $\psi(s) = \log s$ | Likelihood of a mixture; k-means in the limit | **[proved]** tested |
| S-shaped | Convex, then concave | Not submodular: synergies; no guarantee here | **[fact]** tested |
| Decreasing | Harm | With a convex harm, a corner is optimal | **[sketch]** one law tested |

**Why concavity spreads emitters**: with a linear $\psi$ the gain is a sum of
separate terms, so nothing keeps two emitters apart. Spreading comes from $\psi$.

## Notable special cases

- **Independent chances**: $1 - e^{-s} = 1 - \prod_y e^{-\varphi}$ reads as "at
  least one succeeds", with $p_y = 1 - e^{-\varphi}$. Lifeguards and detectors.
- **Maximum coverage**: $\varphi = 1_{d \le R}$ and $\psi = \min(1, s)$. The only
  class with a [proved optimum](../../../docs/benchmark/certified-method.md) today.
- **Thomson and repulsion**: for $\psi = 2s - s^2$, the gain is
  $2 \sum_y \int a_y \, d\mu - \sum_{y, y'} \int a_y a_{y'} \, d\mu$.
- **Mixture likelihood**: for $\psi = \log$ and a normalized $\varphi$, with a
  measured density as $\mu$, the gain is a Poisson likelihood up to a constant
  (**[sketch]** not tested; only the limit below is).
- **k-means**: $\frac{1}{\beta} \log \sum_y e^{-\beta d^2} \to -\min_y d^2$.
- **Rivals**: $\psi_x(s) = s / (s + r(x))$ is concave at each place when rivals stay
  fixed, so the master result holds with a $\psi$ that depends on $x$.

## Classes of $\varphi$

| Class | Constraint | Consequence |
| --- | --- | --- |
| Indicator | $1_{d \le R}$ | Gradient zero almost everywhere; a finite problem |
| Compact | $\varphi = 0$ past $R$ | Blind past its reach: the local minima of garden |
| Fast decay | Gaussian | Numerically blind far away |
| Heavy tail | $1 / d^2$ | Feels everything; walls still trap it |
| $L$-Lipschitz | $\lvert \varphi' \rvert \le L$ | A grid bound, without walls: see below |

## The guarantees, measured

**[measured]** The online bound (Leskovec et al., 2007) is
$\mathcal G(S) + \sum$ of the $k$ best increments, valid from any placement $S$.

| Case | Relocation | Best bound | At most below the best on the grid | Classic $1 - 1/e$ |
| --- | ---: | ---: | ---: | ---: |
| Beach | 0.1425 | 0.1916 | 25.6% | 36.8% |
| Marina | 0.2780 | 0.3674 | 24.3% | 36.8% |

- **It is loose**: true, and far above the real gap, which is unknown on these laws.
- **It stops at the grid**: a placement off the grid may pass it.

**[proved]** Without walls, a gain with Lipschitz laws extends it off the grid:
$\mathcal G^\star \le \text{bound} + k \, L_\psi L_\varphi \, h / \sqrt 2$ on a
grid of step $h$, for a normalized $\mu$. A sharp wall breaks it: the gain jumps.

## Outside these classes

**[fact]** Interference (`Pairs`) is not a function of the sum of signals, and a
max-min objective is not an integral: the master result says nothing about them.
