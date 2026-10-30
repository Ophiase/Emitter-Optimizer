# Manifolds, periodic cells, quotients

**[sketch]** The general form of the map is a Riemannian manifold with a
measure: a domain `M`, a metric `g`, a density `mu`, and a distance that is
the geodesic distance of `g`. The plane is the flat case; the crystal is the
quotient of the flat case by a lattice.

## Why a manifold

- **The surface of an object**: a sphere, a torus, a part in CAD; the
  distance is geodesic, not the chord.
- **A periodic crystal**: the local behaviour repeats, so the domain is
  `R^3 / L` with a lattice `L`; the torus is the exact object, not an
  approximation of an infinite crystal ([crystals](crystals.md)).
- **A chart**: a map sheet in a GIS is a chart; the metric encodes the
  projection.

## What the math becomes

$$
\mathcal G(U) = \int_M
  \psi\!\left(\sum_{y \in U} \varphi\bigl(d_g(x, y)\bigr) \, pass_C(x, y)\right)
  d\mu(x).
$$

- `d_g` is the geodesic distance, so `grad d_g` is the Riemannian gradient
  (the direction of the geodesic from `x` to `y`, with the inverse metric).
- On a quotient, the sum over `y in U` becomes a sum over the images of `y`
  in the lattice: a **lattice sum**, truncated or resummed (Ewald).
- The optimizer needs the Riemannian gradient or a projection
  ([constraints](constraints.md)); the Euclidean formula is a special case,
  which is why the current code can stay flat.

## [sketch] How to keep one engine

Two strategies, behind one interface:

```python
class Domain(Protocol):
    def points(self) -> Points: ...  # where the gain is evaluated
    def measure(self) -> Weights: ...  # mu, the density
    def distance(self, a: Points, b: Points) -> Distances: ...
    def project(self, y: Points) -> Points: ...  # back onto the domain
```

- `Plane`, `Mesh`, `Torus(lattice)`: each one answers the four calls.
- The sum, the laws and the optimizer do not know which one they use.

## [caution]

A chart with a singularity (a pole) is not a manifold; a mesh with a poor
triangulation is not a metric space with a stable geodesic. The benchmark must
show the error of the discrete distance, not only the gain.
