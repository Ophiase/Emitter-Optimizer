# The kernel [decided]

The author's decisions of 2026-10-31, recorded before the migration. They
override the 2.x pages that argued for NumPy and no framework.

| Decision | Consequence |
| --- | --- |
| **JAX and optax are the engine** | `jax.value_and_grad` gives the gradient; `optax` the step; `lax.scan` the loop |
| **Laws are `jax.numpy`, `eval` only** | no `derivative`, no finite differences, no NumPy in `kernel/` |
| **Matplotlib is out, permanently** | a renderer of our own (phase 3) |
| **OpenCV is out** | `jax.image.resize` and Pillow replace it (phase 4) |
| **Walls are an absorption field** | `Segments` stays the exact reference; `Absorption` is the engine |
| **The window and a Rust kernel are open** | phase 5; the author decides |
| **An is-a hierarchy is an ABC** | `Occlusion` is an `ABC`, `HardOcclusion` and `SoftOcclusion` subclass it, one per file |

The kernel is the reference for everything that follows: `shapes`,
`laws`, `scene`, `occlusion`, `coverage`, `descent`. The old `engine/` is
deleted whole at phase 2, never kept as a shim.

A rule that no check enforces is a wish: `just agent::smells` counts the
2024 shapes, every phase lowers it, and it joins `just guards` at zero.
