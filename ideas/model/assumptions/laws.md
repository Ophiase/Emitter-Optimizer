# The two laws: what their shape gives

**The shape of $\psi$ decides the guarantee; the shape of $\varphi$ decides what
a gradient can see.** Claims marked tested are in
`tests/kernel/test_law_classes.py`.

Write $a_y(x) = \varphi(d(x, y)) \, pass_C(x, y)$, the signal of one emitter.

## The master result

**[proved]** If $a_y \ge 0$, $\mu \ge 0$ and $\psi$ is concave, then $\mathcal
G$ is submodular: an emitter helps a large set no more than a small one.

- **Proof**: at each $x$, a concave function of a sum of non-negative terms has
  diminishing increments; integrating against $\mu \ge 0$ keeps them.
- **It never uses** the distance, the walls or the dimension. They only change
  the $a_y$, so the result holds on a sphere, in a building and on a calendar.
- **If $\psi$ is also non-decreasing**, the gain is monotone, and greedy reaches
  $1 - 1/e$ of the optimum among candidates (Nemhauser, Wolsey and Fisher,
  1978).

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
separate terms, so nothing keeps two emitters apart. Spreading comes from
$\psi$.

## Notable special cases

- **Independent chances**: $1 - e^{-s} = 1 - \prod_y e^{-\varphi}$ reads as "at
  least one succeeds", with $p_y = 1 - e^{-\varphi}$. Lifeguards and detectors.
- **Maximum coverage**: $\varphi = 1_{d \le R}$ and $\psi = \min(1, s)$. The
  only class with a [proved
  optimum](../../../docs/benchmark/certified-method.md) today.
- **Thomson and repulsion**: for $\psi = 2s - s^2$, the gain is $2 \sum_y \int
  a_y \, d\mu - \sum_{y, y'} \int a_y a_{y'} \, d\mu$.
- **Mixture likelihood**: for $\psi = \log$ and a normalized $\varphi$, with a
  measured density as $\mu$, the gain is a Poisson likelihood up to a constant
  (**[sketch]** not tested; only the limit below is).
- **k-means**: $\frac{1}{\beta} \log \sum_y e^{-\beta d^2} \to -\min_y d^2$.
- **Rivals**: $\psi_x(s) = s / (s + r(x))$ is concave at each place when rivals
  stay fixed, so the master result holds with a $\psi$ that depends on $x$.

## Fading emitters

**[sketch]** Name proposed for the author to confirm: a **fading** emitter sends
less the further away: $\varphi$ is non-increasing. It is a strong assumption,
and every published case makes it (tested on the five photographs).

**Not fading**, and real enough:

| Emission | Why | Row |
| --- | --- | --- |
| A ring | A rotating sprinkler can leave its foot dry | 2 |
| A lamp under its own shade | The foot of a pole can be darker than beside it | 13 |
| Seeds on the wind | They land at a distance, not at the tree | 12 |
| Waves that interfere | The signal rises and falls with distance | 33 |
| A shop or a bin too close | Nobody wants it at their door | 50 |

**What fading gives**, when $\psi$ is non-decreasing:

- **[proved]** **Stay in the hull**: without walls, on a convex map, an emitter
  can be moved into the convex hull of the demand without loss. Projecting onto
  a convex set brings it closer to every point of that set. A ring breaks this
  (tested).
- **[proved]** **A pull toward demand**: the gradient is a positive sum of unit
  vectors pointing at the demand. Only walls and saturation stand in its way.
- **[proved]** **A mixture of disks**: $\varphi(d) = \int 1_{d \le r} \,
  d\nu(r)$ with $\nu = -d\varphi \ge 0$ (tested). So fading is what relates
  every law to the disks of the exact solver.
- **[proved]** **A known ceiling**: no place receives more than $k \,
  \varphi(0)$.

## How far the signal reaches

Two shapes, and the difference is what the problem can do:

| Class | Constraint | Example | Consequence |
| --- | --- | --- | --- |
| Indicator | $1_{d \le R}$ | A guard's sight | Gradient zero almost everywhere; a finite problem |
| Finite reach | $\varphi(d) = 0$ past $R$ | Water from a sprinkler | Blind past $R$; two emitters past $2R$ do not interact at all |
| Fast decay | Gaussian | A lifeguard's chance | Numerically blind far away |
| Tail to zero | $\varphi > 0$, $\varphi \to 0$ | Wi-Fi power | Feels everything; all emitters interact a little |

- **[proved]** **A finite reach splits the problem**: emitters more than $2R$
  apart add up exactly (tested); with a tail they do not.
- **[proved]** **A tail is a finite reach, up to an error**: if $\varphi <
  \varepsilon$ past $D$, cutting it at $D$ changes the signal by at most $k
  \varepsilon$, so the gain by at most $k \varepsilon L_\psi$ for a normalized
  $\mu$.
- **[fact]** `plants` uses a Gaussian today, so its water never quite stops.
  Only `garden` has a true reach ([question](../../open.md)).

## Tiers

**[sketch]** Wi-Fi's power falls smoothly, while its throughput falls in tiers.

So the tiers are in $\psi$, not in $\varphi$: a staircase with a jump at each
tier. The smooth logarithm of `marina` is only its outline.

- **A gradient sees nothing on a stair**, as on a threshold.
- **The envelope below still gives a bound** (tested on a staircase).

## The guarantees, measured

**[measured]** The online bound (Leskovec et al., 2007) is
$\mathcal G(S) + \sum$ of the $k$ best increments, valid from any placement $S$.

**[proved]** **Any sensor gets one**: replace $\psi$ by $\hat\psi$, its smallest
concave, non-decreasing majorant on $[0, k \varphi(0)]$.

Then $\mathcal G_\psi \le \mathcal G_{\hat\psi}$, and the online bound holds on
the right. This covers domes, thresholds and tiers (`ConcaveEnvelope`, tested).

| Case | $\psi$ | Best published | Bound | At most below the best on the grid |
| --- | --- | ---: | ---: | ---: |
| Ramparts | S-shaped | 0.3580 | 0.3728 | 4.0% |
| Beach | Saturating | 0.1425 | 0.1916 | 25.6% |
| Marina | Saturating | 0.2781 | 0.3760 | 26.0% |
| Harbor | S-shaped | 0.2252 | 0.3047 | 26.1% |
| Garden | Dome | 0.0622 | 0.1137 | 45.3% |

- **It holds on real laws**, where nothing was proved before.
- **It is loose**: far above the true gap, which stays unknown on these laws.
- **It stops at the grid**: a placement off the grid may pass it.
- **The bound is taken from greedy**, in single precision; four digits, no more.

**[proved]** Without walls, a gain with Lipschitz laws extends it off the grid:
$\mathcal G^\star \le \text{bound} + k \, L_\psi L_\varphi \, h / \sqrt 2$ on a
grid of step $h$, for a normalized $\mu$. A sharp wall breaks it: the gain
jumps.

## Outside these classes

**[fact]** Interference (`Pairs`) is not a function of the sum of signals, and a
max-min objective is not an integral: the master result says nothing about them.
