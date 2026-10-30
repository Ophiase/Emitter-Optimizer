# Baselines

**[sketch]** A gain without a reference is a number. The classical placement
problems give three references, and a fourth from the same family as ours.

## The references

| Method | What it optimizes | Why it is a fair reference |
| --- | --- | --- |
| **k-center** | the worst-covered cell | the same map, the same k, a different notion of best |
| **k-median** | the total distance to the nearest centre | the closest classical analogue of a mean gain |
| **Greedy maximum coverage** | the weight covered by k sets | the direct competitor, with binary coverage |
| **Lloyd / Voronoi** | an even spread | the cheap heuristic a team would write by hand |

## How to compare

- Same grid, same density, same obstacles, same number of emitters.
- Same budget of gain evaluations, or report both the time and the
  evaluations.
- Three numbers per run: the gain, the spread (how far the emitters are from
  the demand), and the time.
- Several seeds, and a seed fixed in the table.

## [caution]

k-center and k-median on a continuous map need their own solver; a discrete
greedy on the grid is an approximation and must be labelled as one. The
comparison is only honest if the baseline is not handicapped.
