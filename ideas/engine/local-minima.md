# Local minima

**[measured]** A gradient only feels the slope under an emitter, so a descent
stops on the nearest hill. A relocation jumps past it, and is the default way
out ([results](../../docs/local-minima.md)).

## The trap

- **Compact laws**: past its reach an emitter sends nothing, so it feels nothing.
- **Crowding**: two emitters on one peak, with another peak unserved.
- **Walls**: the gain jumps across a wall; soft walls only blur the step.

## What was tried

- **Several starts**: **[measured]** cheap and useful, never a guarantee.
- **A widened law**, tightened in stages: **[measured]** beats the descent alone,
  loses to a relocation on beach and marina, ties it on harbor. Not kept.
- **A relocation**: **[measured]** move one emitter to the grid point that helps
  most, while the gain rises; then polish by descent. Kept in
  `kernel/placement/relocation.py`.

## [caution]

- It is the classical interchange local search of the p-median literature,
  **[to check]** Teitz and Bart, 1968, applied after a differentiable descent.
- It ends in a local optimum of the jumps: **no proof of a global optimum**.
- One jump pass costs emitters times candidates times points, so it needs a
  candidate list past a few thousand points, as greedy does.
- It evaluates one emitter at a time: a threshold law where two lamps must move
  together can refuse every single jump.
