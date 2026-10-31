# The kernel [decided]

The author's decisions of 2026-10-31, recorded before the migration. They
override the 2.x pages that argued for NumPy and no framework.

| Decision | Consequence |
| --- | --- |
| **JAX and optax are the engine** | `jax.value_and_grad` gives the gradient; `optax` the step; `lax.scan` the loop |
| **Laws are `jax.numpy`, `eval` only** | no `derivative`, no finite differences, no NumPy in `kernel/` |
| **Matplotlib is out, permanently** | Pillow draws the map; plotly draws the gain; both local |
| **OpenCV is out** | Pillow resizes; scikit-image finds the contours |
| **Walls are an absorption field** | `Segments` stays the exact reference; `Absorption` is the engine |
| **The local page replaces the window** | FastAPI serves the page; a Rust kernel stays open |
| **An is-a hierarchy is an ABC** | `Occlusion` is an `ABC`, `HardOcclusion` and `SoftOcclusion` subclass it |
| **An abstraction owns its operations** | `classmethod` factories and methods on the class, never a module of free helpers |
| **One class per module, grouped in a package** | `kernel/descent/` holds the loop, its settings, its step and its result |

The kernel is the reference for everything that follows: `shapes`,
`laws`, `scene`, `occlusion`, `coverage`, `descent`. The old `engine/` and `gui/`
are deleted whole, never kept as a shim.

A rule that no check enforces is a wish: `just agent::smells` counts the
2024 shapes, every phase lowers it, and it joins `just guards` at zero.
