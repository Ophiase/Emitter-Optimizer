# Distance

**[sketch]** Today the distance is Euclidean. It is the one thing the user
cannot change, and it should become a strategy.

## Today

`dist(x, y) = ||x - y||_2`, computed on the grid and the emitter positions in
map units. Obstacles do not change the distance: a wall blocks the signal, it
does not lengthen the path.

## [sketch] A strategy

```python
class Distance(Protocol):
    def __call__(self, start: FloatArray, end: FloatArray) -> FloatArray: ...
    def gradient(self, start: FloatArray, end: FloatArray) -> FloatArray: ...
```

Three implementations, in order of usefulness:

1. **Euclidean** — today, fine when the map is flat and small.
2. **Geodesic on a chart** — the map is a chart over a surface, so the
   distance follows the surface; the author's Future Development named the
   Earth's continents as the case ([../model/physics](../model/physics.md)).
3. **Shortest path around obstacles** — a wall lengthens the path instead of
   zeroing it; this changes `pass_C` into a cost, and it is the honest model
   for propagation ([occlusion](occlusion.md)).

## [caution]

A strategy must provide its gradient, or declare that it is only usable with
the finite-difference fallback ([functions](functions.md)). A distance without
a gradient silently falls back to a slow, approximate run.
