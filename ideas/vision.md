# Vision

**[sketch]** A coverage engine small enough to embed, honest enough to trust,
and open enough for an agent to drive.

## For whom

- **Radio and network planners** who place antennas, access points or
  repeaters on a map with walls, and tune a propagation law.
- **Field engineers**: irrigation, lighting, sensors, where a density of need
  and a budget of devices decide the layout.
- **Retail and logistics**: where a set of points captures the most demand
  under a travel or distance model.
- **Researchers and students** who want a differentiable placement problem
  with arbitrary user functions, not a black-box solver.
- **Agents**: an LLM that must propose a layout, weigh candidates and show a
  figure, through a local protocol ([agent-interop](architecture/agent-interop.md)).

## What it promises

1. **One engine, many physics**: the emitter law, the sensor law and the
   distance are the user's; the engine only optimizes ([functions](engine/functions.md)).
2. **Measured, not claimed**: every result comes with its gain, its seed and
   a figure, and every method is compared to a baseline ([baselines](model/baselines.md)).
3. **Differentiable where it can be, finite differences where it cannot**: the
   gradient is exact for the built-in laws and approximated for arbitrary
   Python callables ([optimizer](engine/optimizer.md)).
4. **Local-first**: no network call the person did not ask for, no telemetry,
   no fetched font or script ([zero-telemetry](architecture/zero-telemetry.md)).
5. **Agent-native**: the engine is headless and speaks JSON; the window is one
   client among others ([layers](architecture/layers.md)).

## What it is not

- **[defined]** Not a GIS: no map projection zoo, no data portal. A density
  grid, a set of segments, and that is the map.
- **[sketch]** Not a deep-learning project. No training, no dataset, no GPU
  requirement; a DL framework only enters as an optional autodiff backend.
- **[sketch]** Not a UI-first product. The window exists to make the engine
  legible, not the other way around.
