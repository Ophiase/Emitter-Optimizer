# Stack

**[sketch]** Python stays: the user writes physics in Python, and the hot loop
is NumPy, not the interpreter. Each piece is the best of its kind for one job,
and the core carries as few as it can.

## The core

| Piece | Why this one |
| --- | --- |
| **Python 3.14** | The author's language; the user's laws are Python callables |
| **NumPy** | The gain is three broadcast arrays; the GIL is released |
| **A step of optimizer** | Projected gradient or `scipy.optimize.minimize` with bounds; no framework |

**[caution]** TensorFlow is out: 600 MB, a release candidate for 3.14, a
retraced graph and autograph warnings for a problem with fifteen variables.
Keras goes with it. PyTorch and JAX stay optional extras, never requirements:
JAX only when a traceable `phi` or `psi` makes `jax.grad` worth it
([functions](../engine/functions.md)).

## The faces

| Face | Stack |
| --- | --- |
| Command line | `argparse` or `typer`, JSON out, CSV and PNG beside it |
| Local service | FastAPI and uvicorn, pydantic models at the boundary and a pydantic-settings config ([agent-interop](agent-interop.md)) |
| Window | DearPyGui, a client of the engine; a thin local page is a question ([open](../open.md)) |
| Figures | `matplotlib` to PNG now; a hand-written SVG renderer is a question |

## Around the code

| Need | Tool |
| --- | --- |
| Environment | `uv`, `pyproject.toml`, `uv.lock` |
| Recipes | `just`, every recipe with its `[doc]` |
| Style, types, tests | `ruff`, `ty`, `pytest` |
| Markdown, TOML | `rumdl`, `taplo` |
| Gate | `just agent gate` |

## [caution] What stays out

No GPU requirement, no network at runtime, no build step for the face, no
second language in the core path. Each of those would make the engine harder
to embed — and the engine is the product.
