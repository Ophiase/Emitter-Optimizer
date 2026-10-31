# Small circuits, interference, layouts

**[sketch]** A small circuit is a 2.5D or 3D placement problem where the
emitters interact: two traces couple, two antennas interfere, two components
cannot touch. This is the case where the gain stops being a sum of
independent emitters.

## What the model needs

- **A pairwise term**: destructive interference, coupling, or a repulsion,
  written `kappa(y_i, y_j)`. The gain becomes

$$
\mathcal G(U) = \sum_{x} \psi\!\left(\sum_{i} \varphi_i(x)\right) \mu(x)
  - \sum_{i < j} \kappa(y_i, y_j).
$$

  which is the energy of a Markov random field with a continuous state: unary
  plus pairwise.

- **Keep-out zones and layers**: the map is a set of allowed regions, not a
  rectangle ([constraints](constraints.md)).
- **A cost per emitter and per via**: the count is part of the answer
  ([emitter-count](emitter-count.md)).

## Cost and structure

The pairwise term is `O(E^2)` per evaluation, against `O(E)` for the sum. At
a few dozen emitters it is nothing; at a thousand it is the whole cost, and a
spatial index or a cutoff radius becomes necessary.

## [caution]

The phase matters for interference: a signal is a complex number, not a
positive amount, and `psi` on a sum of phases is not the same function as
`psi` on a sum of intensities. This is a different model, not a switch.

## [question]

Is this the same project or a second one? The engine, the optimizer and the
protocol are shared; the objective and the physics are new. The answer decides
whether it is a mode of the project or a fork.
