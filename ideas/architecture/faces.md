# Faces

**[sketch]** The kernel computes; a face only displays. What a person sees
should be connectable anywhere, because an engineer working with an agent asks
it to plug a display in rather than opening a program.

## Why not Rust

**[sketch]** The promise is a law the user writes in a few lines, with an exact
compiled gradient. JAX gives that natively; in Rust it means embedding a law
language and a younger autodiff ([language](language.md)).

## Where DearPyGui stops

| Need | DearPyGui | One page, in a tab or a window |
| --- | --- | --- |
| A 2D tool for an engineer | very good, nothing to think about | more work |
| A real 3D view | **[to check]** primitives, no scene | WebGL |
| An agent drives or shows it | no | yes, the service already answers |
| Sharing a result | no | a file or a link |

## The direction

- **[sketch]** One page served by the local service, with its scripts vendored:
  no CDN and no build ([zero-telemetry](zero-telemetry.md)).
- **[question]** A window around that same page, as a thin webview.
- **[caution]** The window has been deleted and restored once already. It stays
  until a spike compares candidates, and only the author removes it.

## What the spike measures

- The orbit of a 64³ field stays fluid.
- Emitters update during a descent.
- It installs through `uv` on Python 3.14, on three systems.
- No telemetry, and nothing fetched at runtime.
