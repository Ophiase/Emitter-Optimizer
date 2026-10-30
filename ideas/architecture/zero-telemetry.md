# Zero telemetry

**[defined]** No network call the person did not ask for: no telemetry, no
analytics, no crash report, no update check, and no font, script or style
fetched from a CDN.

## Consequences

- The fonts in `resources/font/` are local on purpose.
- The local page, when it comes, is plain files served by the service: no
  framework, no build step, no remote asset.
- The service listens on `127.0.0.1` and refuses anything else.
- A benchmark or a figure is computed locally; a published table is generated
  by `just bench`, never uploaded.

## Why

A placement plan can describe a private site — a hospital's antennas, a farm's
irrigation, a shop's catchment. The tool must work on a machine that never
leaves the room.
