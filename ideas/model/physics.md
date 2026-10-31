# Physics

**[sketch]** The engine is agnostic; the model is where a real deployment
lives. Each item below is a candidate, not a promise.

## Signal

- **Anisotropy**: an emitter has a direction and a lobe, so `phi` depends on
  the angle as well as the distance.
- **Path attenuation**: the signal decays along the path, not only with the
  straight-line distance; a wall attenuates instead of blocking
  ([occlusion](../engine/occlusion.md)).
- **Noise floor and probability of detection**: a sensor detects above a
  threshold with a probability, which gives a coverage objective rather than
  a mean ([objective](objective.md)).
- **Several signal classes**: an emitter of class A and a sensor of class B
  do not interact; the gain becomes a sum over pairs.

## Space

- **Surfaces**: if the map is a chart over a manifold, the distance is
  geodesic ([distance](../engine/distance.md)); the Earth's continents were
  the original example.
- **Terrain**: a height field changes both the distance and the visibility.

## [caution]

Every item multiplies the parameters a person must set. Add one only with a
figure that shows what it changes, and a default that reproduces today's
behaviour.
