# The space: map, shadows, manifold, dimension

**The laws say what is rewarded; the space says whether the problem splits, stays
finite, or explodes.** Status per claim; `tests/kernel/test_law_classes.py` holds
the tested ones.

## The map $\mu$

| Constraint | Consequence | Status |
| --- | --- | --- |
| Finite atoms | With disks, a finite set of positions holds an optimum | **[proved]** on paper |
| Continuous density | Partial coverage: that finite set no longer suffices | **[fact]** sourced |
| Grid of cells | Treated as atoms at cell centres, so an approximation | **[fact]** |
| Components further than $2R$ apart | The gain adds up; see the split below | **[proved]** |
| Signed | A difference of submodular terms: no guarantee here | **[fact]** |
| Measured | $\mu$ is data, and the positions explain it | **[sketch]** hidden sources |

**[caution]** The proved optimum on a published map is for its cell centres, not
its continuous density. A continuous optimum is another problem.

## The shadows $C$

| Constraint | Consequence | Status |
| --- | --- | --- |
| No walls | $\mathcal G$ is as smooth as the laws; the grid bound holds | **[proved]** |
| Sharp walls | Still submodular, since $a_y \ge 0$; but $\mathcal G$ jumps on shadow edges | **[proved]** tested |
| Absorbing | Still submodular; no jump when the absorption is bounded | **[sketch]** |
| Closed rooms | No sight line between rooms: the gain adds up | **[proved]** tested |
| Disjoint segments | The hypothesis of the finite-set argument | **[fact]** |
| Touching segments, from masks | The bound still holds; equality must be checked | **[measured]** |

**A gradient cannot see a shadow edge**: it is a jump, not a slope. That is why
the descent blurs walls, and why it cannot cross them without a jump.

### When the problem splits

**[proved]** If the map falls into parts that no emitter can serve together, then
$\mathcal G(U) = \sum_r \mathcal G_r(U_r)$. Solve each room for each budget, then
share $k$ between rooms by dynamic programming. **[sketch]** Not implemented.

## The manifold $E$

| Constraint | Consequence | Status |
| --- | --- | --- |
| Homogeneous, uniform $\mu$ | $\int a_y \, d\mu$ does not depend on $y$; only the pair term remains | **[proved]** sphere |
| Compact, no boundary | No projection, no edge effect | **[fact]** sphere, torus |
| Boundary | An emitter near it loses part of its reach | **[sketch]** |
| Sphere | A geodesic disk is a circle, so Church's crossings should carry over | **[to check]** |
| Torus, reach below half a period | No emitter meets its own image | **[sketch]** |
| Road network | A metric with few geodesics; many facility-location results apply | **[to check]** |

## The dimension

| Quantity | Grows as | Status |
| --- | --- | --- |
| Cells of a grid of step $h$ | $(L / h)^D$ | **[fact]** |
| Crossings for disks, $n$ points | $n^D$, from $D$ spheres meeting | **[to check]** |
| Volume of a ball | $R^D$, so the reach loses meaning in many dimensions | **[fact]** |

- **In two dimensions**, the exact solver runs. It is the only dimension measured.
- **In many dimensions**, no grid survives. Candidates must be real items, which
  is the discrete problem, and the master result still applies.
