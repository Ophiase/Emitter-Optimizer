# Stack [decided]

Python stays as the host; the engine is JAX. A dependency is a promise kept by
someone else, and the core keeps two: `jax` and `optax`.

## The core

| Piece | Why this one |
| --- | --- |
| **JAX** | `value_and_grad`, `jit`, `vmap`, `lax.scan`; one program, CPU or GPU |
| **optax** | Adam, AdamW, Nadam, Lion, SGD behind one interface |
| **Pillow** | reading a map and writing a PNG; not a plotting stack |

## The faces

| Face | Stack |
| --- | --- |
| Command line | `argparse`, JSON out, CSV and PNG beside it |
| Local service | FastAPI and uvicorn; pydantic at the boundary; pydantic-settings for the host and the port |
| Window | Dear PyGui, a thin client of the session; a local page is the alternative (phase 5) |
| Figures | a renderer of our own: PNG with Pillow, SVG by hand (phase 3) |

## Around the code

| Need | Tool |
| --- | --- |
| Environment | `uv`, `pyproject.toml`, `uv.lock` |
| Recipes | `just`, every recipe with its `[doc]` |
| Style, types, tests | `ruff` (including `ANN`), `ty`, `pytest` |
| Markdown, TOML | `rumdl`, `taplo` |
| Gate | `just agent gate` |

## Out

- **Matplotlib**, everywhere and permanently.
- **OpenCV**: `jax.image.resize` and Pillow do its two jobs.
- Any network call at runtime; any build step for a face.
