# The sphere: a case with a known answer

**[sketch]** A sphere is the first manifold because its optimum is known. A
gain that finds a regular polyhedron by itself, with nothing about polyhedra in
the code, is evidence a table cannot give.

## The setting

- **Domain**: the unit sphere, uniform density, no walls.
- **Distance**: the geodesic angle $d(x, y) = \arccos \langle x, y \rangle$.
- **Emitter**: the von Mises-Fisher law
  $\varphi(d) = e^{\kappa (\cos d - 1)}$.
- **Sensor**: the quadratic law $\psi(s) = 1 - (1 - s)^2$.

## Why the optimum is known

**[proved]** Expanding the square turns the gain into a pair energy.

$$
\mathcal G(U) = \text{const} + 2 \sum_{y} \int \varphi_y
  - \sum_{y, y'} \int \varphi_y \varphi_{y'} .
$$

- $\int \varphi_y$ does not depend on $y$, by symmetry.
- So maximizing $\mathcal G$ minimizes
  $\sum_{y \neq y'} f(\langle y, y' \rangle)$, where $f$ is the integral of
  the product of two laws.
- With $t = \langle y, y' \rangle$, a product of two such laws is again the same
  law, of concentration $\kappa \sqrt{2 + 2 t}$. Up to constants:

$$
f(t) \propto \frac{\sinh u}{u}, \quad u = \kappa \sqrt{2 + 2 t} ,
$$

a power series in $2 + 2t$ with positive coefficients.

- **[to check]** That makes $f$ completely monotonic in the squared distance, the
  hypothesis of Cohn and Kumar's *universally optimal* configurations, which
  include the tetrahedron, the octahedron and the icosahedron.

## What the test asserts

| Emitters | Expected | Smallest angle between two emitters |
| --- | --- | --- |
| 4 | tetrahedron | 109.47° |
| 6 | octahedron | 90.00° |
| 12 | icosahedron | 63.43° |

## [caution]

- The grid discretizes the integral, so the angles hold within a tolerance.
- A descent can stop in a local optimum: the test uses several starts.
- With another sensor law the gain is no longer a pair energy, and the optimum
  is no longer known.
