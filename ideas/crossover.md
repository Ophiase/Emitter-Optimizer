# Crossover with the point-cloud project

**[sketch]** Both projects answer a question about **where things are**: one
recovers the pose of a rigid object from a scan, the other chooses where to put
emitters. They share a metric space, an occlusion, an optimization over
positions, and an agent layer. Three crossovers are worth a look, the first
being the one with a real claim.

## 1. Place the markers so that the pose is observable

The point-cloud project aligns a scan to a model and reports which motions the
data leaves free: its **observability**. A camera sees a few fiducial markers
on a part and must recover its pose. Where should the markers go?

- **Domain**: the surface of the part, a mesh ([manifolds](model/manifolds.md)).
- **Emitters**: the markers, constrained to the surface.
- **Demand**: the viewpoints the camera may take, weighted by how often they
  occur.
- **Visibility**: a marker is seen from a viewpoint if the segment does not
  cross the part ([occlusion](engine/occlusion.md)).
- **Gain**: not a coverage of places, but the **observability** the marker set
  gives: the smallest eigenvalue of the information matrix over the viewpoint
  set, or the worst pose uncertainty. That is the quantity the point-cloud
  project already computes.

This is the crossover with a claim: *a placement chosen to maximize a
min-observability objective beats a hand-placed marker set*, measured on their
synthetic scenes with a known truth. It uses our optimizer and their metric,
and neither alone answers it.

## 2. Cover the surface of a scanned part

Align the scan to the CAD model with the point-cloud project, take the mesh as
the domain, and place inspection points, lights or sensors so that every face
is seen or lit from at least one place. The distance is geodesic
([distance](engine/distance.md)); the visibility is the same ray test; the
demand is a per-face weight. This is the **surface case** of the roadmap, with a
real input instead of a synthetic mesh.

## 3. An emitter array is a rigid body

An antenna array, a camera rig, a set of sensors on one bracket: the emitters
move together. Their positions are `q + R r_i`, six numbers; the projection
back onto a rigid motion is the **Kabsch/Umeyama** closed form the point-cloud
project already has ([constraints](model/constraints.md)). Our constrained
optimizer would use their retraction instead of writing one.

## What not to share yet

- No code copy without reading both guards; the Rust core only if a shared
  geometry crate earns it ([language](architecture/language.md)).
- No shared dependency on a deep-learning framework: neither project needs one
  for its core.

## The first experiment

A square plate, four markers, sixteen viewpoints around it. Place four markers
with our engine (surface domain, min-observability gain), measure the pose
error over the viewpoints with the point-cloud project's estimator, and compare
with the four corners. If the worst-case error drops, the crossover is a paper;
if it does not, the idea is closed in one afternoon.
