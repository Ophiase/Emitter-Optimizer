# A proved optimum for coverage with walls

**[defined by the run, for the author to confirm]** The short-term goal: place
emitters that cover a disk, behind walls, in continuous space, and **prove** how
far any placement is from the best one.

## Why this goal

**[fact]** What an outside reviewer finds weak in the project:

- Its gains are scores with no scale; `0.0622` means nothing alone.
- Its references are random and greedy, and greedy is not an optimum.
- The README says it plainly: no proof of a global optimum.
- The maps are hand-painted over photographs, and the laws are illustrative.

**[fact]** What exists, as read on 2026-11-05 (sources below):

| Tool or work | What it does | What it leaves open |
| --- | --- | --- |
| spopt (PySAL) [1] | Maximal covering, exact | Sites are a finite set given in advance |
| Church's circle intersections [2] | A finite set that solves the plane exactly | Stated for no obstacles |
| Line-of-sight coverage, IJGIS 2023 [3] | Continuous, with obstacles | A heuristic, per its abstract |
| Wi-Fi planner by annealing [4] | Floor plan and walls | Its README reports no bound |
| Commercial GIS location tools [5] | Widely used | Rarely reproducible, per the abstract |
| Sensor placement in polygons [8] | Continuous, range-limited, with holes | Minimum sensors, by heuristics |
| Dispersive art gallery [9] | Exact, with holes | Guards on vertices, another objective |

**[caution]** The need is inferred, not reported. No practitioner was asked, and
no source says "I need this". What is sourced is the gap: we found no tool that
gives a proved optimum with walls in continuous space. We did not prove none exists.

**[caution]** This is probably not new mathematics. It joins Church's set to the
arrangements of visibility regions that the art gallery community already uses.
The contribution to defend is an open, measured, checkable tool, not a theorem.

## For whom

- **Researchers** in continuous location: instances with known optima and walls,
  to test a heuristic against, in a file that needs no code of ours.
- **Engineers** with a plan already made: how far below the optimum is it, at most?
  This holds only if their question is really a disk and a wall.

## The alternatives set aside

| Alternative | Why not now |
| --- | --- |
| A real Wi-Fi validation against measurements | Needs data and a site; not reachable in a session |
| Differentiable radio on Sionna RT [6] | It is already a mature library; we would be a thin client |
| Submodular online bound [7] on the published laws | Needs a concave law: `garden` and `harbor` are not |
| Publish on PyPI with a polished page | Packaging without a result shows nothing new |
| More cases from the catalogue | More of what the project already has too much of |

## What success means

Every criterion is a number a third party can regenerate with `just certify`:

1. **Proof**: at least 90% of 180 reference instances end with the lower bound
   equal to the upper bound.
2. **The bound holds**: no search passes it, and removing any class of candidates
   makes it false on an instance the tests name.
3. **The file stands alone**: the reference set re-scores with `Instance` alone,
   and the test suite checks that the stored optima still solve to the same value.
4. **The engine is measured**: its gap to the optimum is published as it is,
   whether good or bad, next to discrete solvers on the same instances.
5. **A person can use it**: `emitter-optimizer exact` judges their own plan.

## The model

**[defined]** Integer weights on points, a radius, disjoint segments, `k`
emitters in a rectangle. A point is covered if an emitter is within the radius
and their sight line properly crosses no wall.

**[sketch]** The finite set extends Church's: the crossings of circles, walls,
map edges and shadow edges, plus wall ends and the points. A crossing on a wall
is taken once per side.

**[to check]** The reasoning for this set is ours and is not peer-reviewed; the
tests attack it, they do not prove it. The method page states the argument.

## Sources

1. spopt, maximal covering notebook: <https://pysal.org/spopt/notebooks/mclp.html>
2. Blanco and Gázquez, 2020, citing Church: <https://arxiv.org/abs/2005.03274>
3. Line-of-sight coverage, IJGIS 2023: <https://doi.org/10.1080/13658816.2023.2193829>
4. Wireless Access Point Optimization:
   <https://github.com/samuelterra22/Wireless-Access-Point-Optimization>
5. Reproducibility of location models, 2021, abstract only:
   <https://doi.org/10.1007/s10109-021-00350-w>
6. Sionna RT: <https://arxiv.org/abs/2303.11103>
7. Leskovec et al., 2007, online bounds: <https://www.cs.cmu.edu/~jure/pubs/detect-kdd07.pdf>
8. Mikula and Kulich, omnidirectional sensor placement: <https://arxiv.org/abs/2410.08784>
9. Fekete et al., 2025, guarding offices: <https://arxiv.org/abs/2506.21307>
