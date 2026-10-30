# Crystals and periodic cells

**[sketch]** A crystal repeats, so the local behaviour is the whole story: the
domain is a torus, the emitters are atoms, and the physics is the one of the
author's crystallography project (a non-Gaussian displacement density per
atom). The idea is to place or displace atoms so that some property is
maximized, on a periodic cell.

## What the project already has

A crystal of urea, atomic displacement densities that are true probabilities,
and a Fourier transform that is exact in the model. That code is a reference,
not a dependency: no data and no code move between the two projects without a
reason ([../../AGENTS.md](../../AGENTS.md)).

## The placement problem, stated

- **Emitters are atoms**: one point per atom in the cell, plus the images in
  the lattice.
- **The constraint is kinematic**: an atom in a molecule has fixed bond
  lengths and angles; only its torsion or the rigid motion of a group moves.
  A displacement density is a *distribution* over positions, not a point
  ([constraints](constraints.md)).
- **The signal is an interaction**: this is the case where summing
  independent emitters is not enough; a pair term enters
  ([circuits](circuits.md), [physics](physics.md)).
- **The domain is periodic**: a lattice sum, truncated or resummed, replaces
  the plain sum ([manifolds](manifolds.md)).

## Why it is interesting

- The periodic case is a clean, testable mathematical object: a torus, a
  lattice, a known limit when the interaction range is small.
- The displacement density gives a **stochastic emitter**: the gain is an
expectation over the atom's position, which is a convolution with the density
  (or a Monte Carlo average), and that is a new, well-posed quantity.
- It connects the project to a real physical question the author already
  works on, instead of a synthetic demo.

## [question]

What is maximized, physically? A diffraction signal, a stability, a desired
defect arrangement? Without that, the case is a mathematical toy — a good one,
but a toy.
