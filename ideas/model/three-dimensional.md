# The three-dimensional case

**[sketch]** The default window draws a plane. Nothing in the gain requires
two dimensions: the same sum works on a volume, on a surface, or on a mesh.
The question is which cases pay for the extra work.

## What changes

| | Plane (today) | Volume | Surface |
| --- | --- | --- | --- |
| Domain | `(rows, columns)` | `(depth, rows, columns)` | a triangle mesh |
| Density | one weight per cell | one weight per voxel | one weight per vertex or face |
| Obstacles | segments | surfaces | edges on the mesh |
| Distance | Euclidean | Euclidean | geodesic ([distance](../engine/distance.md)) |
| Cost | `R C` | `R C D` | `faces` |

The gain is unchanged; only the set of evaluation points and the distance
change. A 64³ volume is 262 000 cells, a thousand times the demo map: the
benchmark must say whether the optimizer is still fast enough
([../architecture/stack](../architecture/stack.md)).

## The cases that motivate it

- **A building**: emitters (Wi-Fi, smoke detectors, lights) placed in rooms on
  several floors; density is people per voxel, walls are surfaces.
- **A machine or a part**: sensors on the surface of a component, density is
  the surface, distance is geodesic.
- **A circuit or a photonic chip**: a thin 3D structure with layers.
- **A crystal**: a periodic volume, treated as a torus
  ([manifolds](manifolds.md), [crystals](crystals.md)).

## [caution]

A 3D value map cannot be shown as one image. A window shows slices, or an
isosurface; a figure is a slice plus a projection. This is the cost of the
case, and it is a UI cost, not a mathematical one.

## [question]

Which one first: a surface (geodesic distance, no volume) or a volume (more
cells, no geodesic)? The surface is the natural extension of the current
code; the volume is the natural extension of the user's mental picture.
