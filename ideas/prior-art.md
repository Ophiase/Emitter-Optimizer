# Prior art

**[to check]** Claims to verify before writing them in a paper or a README.

## Placement and coverage

- **Facility location**: k-center and k-median, the two classical answers;
  both are NP-hard, both have approximation algorithms, both ignore an
  arbitrary sensor law. A baseline, not a competitor.
- **Maximum coverage**: choose k sets to cover the most weight; greedy gives
  `1 - 1/e`. The closest published formulation to our gain, with binary
  cells instead of a differentiable one.
- **Sensor deployment** literature: grid coverage, probabilistic detection,
  and Voronoi or Lloyd relaxation for even spacing.
- **Optimal experiment design** and **Bayesian optimization**: relevant when
  evaluating the gain is expensive; ours is cheap, so the comparison is a
  cost per gain curve.

## Differentiability

- **Soft visibility / differentiable rendering**: the smooth replacement of a
  binary visibility test already exists in neural rendering; the borrowed
  idea is a temperature that tends to the exact test.
- **Autodiff**: JAX for a traceable user function, PyTorch for a familiar
  one. Both are optional, neither is required by the engine.
- **Straight-through estimators**: a candidate when only the sign of a test
  is differentiable, as with hard visibility.

## Manifolds, lattices, constraints

- **Riemannian optimization**: gradient descent on a manifold, with a
  retraction and a projection; the reference is the matrix-manifold
  literature. Our constraint case is a small instance of it.
- **Ewald summation**: the standard way to sum a periodic interaction; the
  crystal case needs it or a justified truncation.
- **Geodesic distance on meshes**: heat method, exact polyhedral methods,
  graph distances. The choice sets the error of the surface case.
- **VLSI placement**: quadratic placement, force-directed spreading,
  analytical placement (ePlace and relatives). The circuit case is a
  mature field with strong baselines; **[to check]** how much of it applies
  to a pairwise interference term rather than a wirelength.
- **Antenna arrays and beamforming**: anisotropic emitters and interference
  are standard there; **[to check]** which objective they optimize.

## What is ours

**[sketch]** The combination, not the pieces: a user-defined emitter law and
sensor law, a density, segments that block, an exact gradient where the laws
allow it, and an agent protocol around the whole thing. The claim to defend
is *one engine for many physics*, measured against the classical baselines.

## To read

- **[to check]** The coverage formulations used in radio planning, and which
  propagation model they call standard.
- **[to check]** The approximation guarantees of greedy maximum coverage and
  how they compare on a continuous map.
- **[to check]** Any public implementation of differentiable visibility in a
  placement problem, to avoid claiming novelty.
- **[to check]** Riemannian optimization libraries (PyManopt, ROPTLIB) and
  whether one is worth a dependency for the constraint case.
- **[to check]** Whether analytical VLSI placement already covers the
  circuit case, which would make it a demo rather than a contribution.
