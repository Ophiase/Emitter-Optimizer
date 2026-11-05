# The scales: only ratios matter

**[proved]** Stretching every length by the same factor leaves the gain unchanged
(tested). So a problem has no scale of its own, only ratios.

| Ratio | Meaning | Regime |
| --- | --- | --- |
| $\rho = k V_D R^D / \lvert E \rvert$ | Share of the map that disks could cover | Small: emitters ignore each other. Large: saturated |
| $h / L$ | Cell over map | Sets the grid's gap, see below |
| $R / h$ | Reach over cell | Below one, the map misses what an emitter does |
| $\tau / R$ | Blur of a law over reach | Wide: a false optimum. Narrow: no slope |
| $\ell / R$ | Wall length over reach | Short: a nick. Long: a separation |
| $n R^D / \lvert E \rvert$ | Points per disk | Few: combinatorial. Many: near continuous |

## What the measurements say

**[measured]** Exact solutions on a grid, against the proved optimum, on the 180
reference instances, where $\rho = 0.7$. Mean gap:

| Emitters | 16 by 16 | 32 by 32 | 64 by 64 |
| ---: | ---: | ---: | ---: |
| 3 | 5.11% | 3.11% | 1.61% |
| 5 | 4.25% | 2.38% | 1.26% |
| 10 | 4.90% | 2.41% | 1.21% |
| 20 | 4.93% | 1.90% | 0.76% |

- **Halving the cell about halves the gap**, at every number of emitters.
- **$R / h$ does not explain it**: at a fixed grid, $R / h$ goes up as emitters
  go down, and the gap does not fall. Fit over all rows: correlation $-0.47$ only.

**[caution]** On the five published maps as disks, the gap falls steadily with
$R / h$: 16.5% at 3.2, 5.9% at 4.2, 4.8% at 5.0, 0.5% at 12, 0.4% at 25.

It looked like a law. The reference set refutes that reading, and five maps also
differ in walls and in density.

**[measured]** The saturated regime shows on those maps: ramparts, with
$\rho = 3.0$, leaves random 6.0% below the optimum, against 33% to 50% for the
others.

**[measured]** The blur $\tau / R$ was chosen on separate seeds: on the descent
alone, $0.05$ beats $0.2$ in 4 of 6 trials, ties in one and loses in one.

## What to check next

- **[to check]** The gap against $\rho$: the reference set holds it fixed.
- **[to check]** Why few emitters lose more at a fixed $R / h$.
