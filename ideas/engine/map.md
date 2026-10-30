# The map

**[defined]** A map is a rectangle, a grid of weights and a list of segments.
Nothing more: no projection, no file zoo, no metadata.

## Representation

- `grid_size = (rows, columns)` and `map_scale = (width, height)` in map
  units. The two axes are independent: a non-square grid was a bug until
  v2.0.
- `density`: an array of shape `(rows, columns)`, non-negative; it is resized
  to the grid when it comes from an image, and read by nearest cell.
- `obstacles`: a list of segments, normalized to the unit square when they
  come from an image, then multiplied by `map_scale`.
- `initial positions`: drawn uniformly, or from the density, with a seed
  ([optimizer](optimizer.md)).

## Where they come from

| Input | Today | Later |
| --- | --- | --- |
| Density | an image read by OpenCV | an array, a CSV, a function |
| Obstacles | a mask, contoured by OpenCV, or a CSV of segments | the same, plus a distance field for soft occlusion |
| Units | arbitrary; `map_scale` is the only unit | the same |

## [caution]

OpenCV enters for two functions only (Canny and contour extraction). It is a
candidate for removal ([open](../open.md)); the map format must not depend on
it.
