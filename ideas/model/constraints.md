# Constrained emitters

**[sketch]** An emitter is not always a free point. It can be an atom in a
molecule, a component on a board, a sensor on a surface, a site in a lattice.
The constraint is the interesting part: it reduces the dimension and it gives
the physics.

## Kinds of constraint

| Constraint | Degrees of freedom | Example |
| --- | --- | --- |
| Free point on the map | 2 or 3 per emitter | today |
| On a surface | 2 per emitter (a chart) | sensor on a part |
| In a rigid body | 6 for the body, fixed offsets | molecule, antenna array |
| Internal coordinates | bond lengths and angles fixed, torsions free | a molecule |
| A lattice site | discrete choice | a crystal, a chip |
| Keep-out / layers | inequality | a circuit |

## The same gain, a smaller space

If the positions are written `y = F(theta)`, the chain rule gives

```text
dG/dtheta = (dF/dtheta)^T dG/dy
```

so a constrained problem is the same engine with a projection or a
parameterization:

- **parameterization** for a rigid body (`theta` is a rotation and a
translation) or a molecule (`theta` is the torsions);
- **projection** on the domain (a surface, the map's bounds) between two
  steps, which is the projected gradient already planned
  ([optimizer](../engine/optimizer.md));
- **discrete choice** for a lattice site, which is not differentiable: a
  greedy or a rounding after a continuous relaxation
  ([emitter-count](emitter-count.md)).

## [caution]

A constraint can make the landscape worse: a molecule with three torsions can
have several minima per torsion. Multi-start is not optional
([optimizer](../engine/optimizer.md)).

## [question]

Which constraint first? A rigid body is the cheapest to implement (a rotation
and a translation, a known projection) and it is the one the crystal and the
circuit cases both need.
