# Engine — the differentiable gain

**[defined]** The engine answers one question: given a map, a density, a set of
obstacles, an emitter law and a sensor law, where should the emitters go?

- [gain.md](gain.md) — the notation and the function that is maximized.
- [occlusion.md](occlusion.md) — what a wall does, and the smooth version to
  come.
- [map.md](map.md) — the grid, the density, the segments, the units.
- [distance.md](distance.md) — Euclidean today; a strategy later.
- [functions.md](functions.md) — the contract for the user's two laws.
- [optimizer.md](optimizer.md) — how the descent runs, and its bounds.

## The invariant

**[defined]** The engine is pure and headless
([layers](../architecture/layers.md)): it returns values, it prints nothing,
it opens no window, and it does not know that an agent exists.
