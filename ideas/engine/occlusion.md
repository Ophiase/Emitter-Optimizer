# Occlusion [decided]

A wall is matter that absorbs. The engine rasterises the map into an opacity
image, samples `K` points along each sight line, and the visibility is the
transmittance

$$
pass(x, y) = \exp\!\left(-\frac{\lVert x - y \rVert}{K}
  \sum_{k=1}^{K} opacity(x_k)\right),
$$

as in volume rendering. The cost no longer depends on the number of walls; a
map image *is* the field, so no contour extraction is needed; a partial wall
(plaster against concrete) is physics, not a special case.

- `Absorption(opacity, extent, samples)` is the engine; `Absorption.from_segments`
  and `.from_image` build it.
- `Segments(walls, edge)` is the exact reference, used by the tests and the
  benchmark; `edge` is `HardEdge` or `SoftEdge`.
- `Clear` has no walls.
- The descent anneals: `Annealed.at(progress)` blurs the opacity (or the
  segment edge) from 5 % to 0.1 % of the scene; the final score uses the sharp
  version.

A one-pixel wall in a coarse image leaks: its opacity times its thickness must
reach about 5, so the transmittance is below 1 %. A test compares `Absorption`
to `Segments` within 0.05 on every cell, and another proves that the soft
gradient sees the wall the hard one ignores.
