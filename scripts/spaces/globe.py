import argparse
import json
import time
from io import BytesIO
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
from PIL import Image, ImageDraw

from emitter_optimizer.kernel import (
    Coverage,
    Descender,
    DescentSettings,
    Greedy,
    HardOcclusion,
    Physics,
    Sphere,
    Step,
)
from emitter_optimizer.render import GlobeImage
from emitter_optimizer.service.paths import PROJECT_ROOT

CASE = PROJECT_ROOT / "resources" / "cases" / "globe"
FIGURE = PROJECT_ROOT / "docs" / "figures" / "case_globe.gif"
ROWS, COLUMNS = 90, 180
EMITTERS = 12
CITY_SPREAD = 4.0
REACH = 30.0
STEPS = 300
SPIN_FRAMES = 36

PHYSICS = Physics(
    emitter=lambda angle: jnp.exp(REACH * (jnp.cos(angle) - 1.0)),
    sensor=lambda signal: 1.0 - jnp.exp(-signal),
)


def _paint(places: Path, land: Path) -> None:
    """Rasterize the public-domain Natural Earth files into the two layers."""
    latitude = 90.0 - (np.arange(ROWS) + 0.5) * 180.0 / ROWS
    longitude = (np.arange(COLUMNS) + 0.5) * 360.0 / COLUMNS - 180.0
    lat, lon = np.meshgrid(latitude, longitude, indexing="ij")
    people = np.zeros((ROWS, COLUMNS))
    for feature in json.loads(places.read_text())["features"]:
        city = feature["properties"]
        across = (lon - city["longitude"] + 180.0) % 360.0 - 180.0
        across = across * np.cos(np.radians(lat))
        squared = (across**2 + (lat - city["latitude"]) ** 2) / CITY_SPREAD**2
        people += city["pop_max"] * np.exp(-squared)
    people = 255.0 * people / people.max()
    Image.fromarray(people.astype(np.uint8)).save(CASE / "attraction.png")
    mask = Image.new("L", (COLUMNS * 4, ROWS * 4), 0)
    draw = ImageDraw.Draw(mask)
    for feature in json.loads(land.read_text())["features"]:
        geometry = feature["geometry"]
        polygons = (
            [geometry["coordinates"]]
            if geometry["type"] == "Polygon"
            else geometry["coordinates"]
        )
        for polygon in polygons:
            ring = [
                ((x + 180.0) * COLUMNS * 4 / 360.0, (90.0 - y) * ROWS * 4 / 180.0)
                for x, y in polygon[0]
            ]
            draw.polygon(ring, fill=255)
    mask.save(CASE / "land.png", optimize=True)


def _layers() -> tuple[Sphere, np.ndarray]:
    people = np.asarray(Image.open(CASE / "attraction.png"), dtype=np.float64) / 255.0
    land = np.asarray(Image.open(CASE / "land.png"), dtype=np.float64) / 255.0
    return Sphere.of(ROWS, COLUMNS, jnp.asarray(people)), land


def _field(sphere: Sphere, positions: jax.Array) -> np.ndarray:
    signal = sphere.signal(PHYSICS.emitter, positions)
    return np.asarray(PHYSICS.sensor(jnp.sum(signal, axis=1))).reshape(sphere.shape)


def main() -> None:
    parser = argparse.ArgumentParser(description="The twelve-station globe case.")
    parser.add_argument("--places", type=Path, help="Natural Earth populated places")
    parser.add_argument("--land", type=Path, help="Natural Earth land")
    arguments = parser.parse_args()
    if arguments.places is not None and arguments.land is not None:
        _paint(arguments.places, arguments.land)
    sphere, land = _layers()
    coverage = Coverage(sphere, HardOcclusion(), PHYSICS)
    draws = sphere.sample(jax.random.key(1), 32, EMITTERS)
    random = float(np.mean([coverage.gain(draw) for draw in draws]))
    started = time.perf_counter()
    candidates = Sphere.of(30, 60).points
    greedy = Greedy(sphere, PHYSICS, candidates).place(EMITTERS)
    greedy_seconds = time.perf_counter() - started
    steps: list[np.ndarray] = []

    def capture(step: Step) -> None:
        steps.append(np.asarray(sphere.project(step.positions)))

    settings = DescentSettings(
        EMITTERS, STEPS, starts=8, report_every=6, step_size=0.01
    )
    started = time.perf_counter()
    free = Descender(sphere, PHYSICS, settings, on_step=capture).run()
    descent_seconds = time.perf_counter() - started
    polish = Descender(
        sphere,
        PHYSICS,
        DescentSettings(EMITTERS, STEPS, step_size=0.003, report_every=50),
        start=greedy[None],
    ).run()
    best = max(free, polish, key=lambda result: result.gain)
    print(
        f"globe random {random:.4f} greedy {float(coverage.gain(greedy)):.4f} "
        f"({greedy_seconds:.0f}s) free {free.gain:.4f} ({descent_seconds:.0f}s) "
        f"polish {polish.gain:.4f}"
    )
    units = np.asarray(sphere.project(best.positions))
    field = _field(sphere, best.positions)
    globe = GlobeImage(field, land, size=460)
    frames = [
        globe.draw(units, longitude=360.0 * index / SPIN_FRAMES, latitude=22.0)
        for index in range(SPIN_FRAMES)
    ]
    buffer = BytesIO()
    frames[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=110,
        loop=0,
    )
    FIGURE.write_bytes(buffer.getvalue())
    np.savetxt(CASE / "stations.csv", units, delimiter=",", header="x,y,z", comments="")


if __name__ == "__main__":
    main()
