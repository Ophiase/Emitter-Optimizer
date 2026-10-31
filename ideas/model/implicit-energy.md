# An implicit energy, not a voxel grid

**[sketch]** The 2D baseline evaluates the gain on a grid. A 3D volume makes
that grid a cube: `N^3` cells, a Riemann sum whose error falls as `h^2` for a
smooth density and as `h` for the binary visibility. Past a few dozen cells per
axis the cost is the model, not the optimizer. The energy has to be evaluated
**as a function**, not voxelized.

## The integral is the object

$$
\mathcal G(U) = \int_M
  \psi\!\left(\sum_{y \in U} \varphi\bigl(d(x, y)\bigr) \, pass_C(x, y)\right)
  d\mu(x).
$$

A grid is one quadrature of this integral. Three others are available, and
none of them needs a volume of cells:

1. **A continuous density**: a sum of kernels, a Gaussian mixture, a coordinate
   network. The integral is then evaluated by Monte Carlo or, better, by
   quasi-Monte Carlo (Sobol): the error is `O(1/sqrt(N))` whatever the
   dimension, and the same seed gives the same points.
2. **Importance sampling**: draw the points from `mu` itself, so the density
   disappears from the sum and the effort follows the demand.
3. **An implicit representation**: a signed distance field for the obstacles
   and a coordinate network (SIREN, a small MLP) for `mu` and the visibility.
   The network is trained on measurements or on a scan; the gain is then a
   differentiable function of the emitter positions **and** of the weights.

## Why it fits this project

The optimizer already works on a set of sample points and a measure; a voxel
grid is only the special case where the points are the cell centres. A `Domain`
strategy ([manifolds](manifolds.md)) that returns `points` and `measure` can
return a QMC sample instead of a grid, without touching the gain, the laws or
the descent.

## [caution] Traps

- **A stochastic gain has a noisy gradient.** Fix the sample across iterations
  (common random numbers), or the descent optimizes the noise. The seed then
  becomes part of the result, as it already is for the initial positions.
- **A learned field is an approximation with its own error.** The voxel grid
  stays the reference: the implicit model is validated against it on a case
  where both exist.
- **The visibility is the hard part.** A binary segment test does not survive
  sampling; it needs a distance field and the smooth version
  ([occlusion](../engine/occlusion.md)), or the estimate is biased near a wall.
- **The cost moves, it does not vanish**: `N` samples times `E` emitters per
  iteration, and a network evaluation if the field is learned.

## Done when

A 3D situation that is out of reach on a voxel grid is optimized with a QMC
sample, the same seed gives the same answer, and the gain agrees with a fine
grid on a small case where the grid is affordable.
