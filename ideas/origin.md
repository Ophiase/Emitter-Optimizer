# Origin

**[defined]** A personal project of 2019–2021: a desktop application that
places emitters on a map so the signal they cover is maximal. TensorFlow 2.14
for the gradient, DearPyGui 1.10 for the window, conda for the environment.
It worked, and then the stack aged faster than the idea.

## What survives

The model, which was the point:

- a gain `G` over emitter positions, differentiable in those positions;
- a density `mu` weighting the map, and segments `C` blocking the signal;
- two functions the user writes, the emitter law `phi` and the sensor law
  `psi` ([gain](engine/gain.md)).

## What goes

- **TensorFlow and Keras** for a problem with fifteen variables: 600 MB, a
  release candidate for Python 3.14, a graph to retrace, and warnings from
  the autograph front end ([stack](architecture/stack.md)).
- **DearPyGui as the product.** A window with no API, no state and no
  headless picture cannot be driven by an agent
  ([agent-interop](architecture/agent-interop.md)). It may stay as a legacy
  viewer for a while.
- **conda, the Makefile and the installer script**, replaced by uv and `just`
  in v2.0.

## The 2026 restart

**[defined]** v2.0 (2026-10-30) is the Kanon migration only: the code runs on
Python 3.14, the package is `src/emitter_optimizer/`, the gate passes. The
behaviour is the same. The modernization of the stack and the model starts at
v2.1, on `dev/engine` ([roadmap](roadmap.md)).
