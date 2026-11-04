import csv
import time
from dataclasses import dataclass
from io import BytesIO

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
    Step,
    Torus,
)
from emitter_optimizer.render import AtomsImage
from emitter_optimizer.render.map import PLASMA
from emitter_optimizer.service.paths import PROJECT_ROOT

CASE = PROJECT_ROOT / "resources" / "cases" / "urea"
FIGURES = PROJECT_ROOT / "docs" / "figures"
CELL = (5.565, 5.565, 4.684)
GRID = (24, 24, 20)
CANDIDATES = (12, 12, 10)
STRIDE = 3
ATOM_WIDTH = 0.35
PILE_UP = 1.0
HEAVY, LIGHT = 8, 8
SEARCH = DescentSettings(HEAVY, 400, starts=12, report_every=8, step_size=0.02)
OXYGEN_ELECTRONS = 8.0
SPIN_FRAMES = 36
MAP_SIZE = 460
EMITTER = "crimson"

OPERATIONS = (
    ((1, 0, 0), (0, 1, 0), (0, 0, 1), (0.0, 0.0, 0.0)),
    ((0, -1, 0), (-1, 0, 0), (0, 0, 1), (0.5, 0.5, 0.0)),
    ((0, 1, 0), (-1, 0, 0), (0, 0, -1), (0.0, 0.0, 0.0)),
    ((-1, 0, 0), (0, 1, 0), (0, 0, -1), (0.5, 0.5, 0.0)),
    ((-1, 0, 0), (0, -1, 0), (0, 0, 1), (0.0, 0.0, 0.0)),
    ((0, 1, 0), (1, 0, 0), (0, 0, 1), (0.5, 0.5, 0.0)),
    ((0, -1, 0), (1, 0, 0), (0, 0, -1), (0.0, 0.0, 0.0)),
    ((1, 0, 0), (0, -1, 0), (0, 0, -1), (0.5, 0.5, 0.0)),
)

PHYSICS = Physics(
    emitter=lambda distance: jnp.exp(-(distance**2) / (2.0 * ATOM_WIDTH**2)),
    sensor=lambda signal: signal - PILE_UP * signal**2 / 2.0,
)


@dataclass(frozen=True, slots=True)
class Atom:
    element: str
    electrons: int
    position: np.ndarray


def atoms() -> list[Atom]:
    """Every atom of the cell, from the published asymmetric unit."""
    size = np.array(CELL)
    found: list[Atom] = []
    with (CASE / "structure.csv").open(encoding="utf-8") as file:
        for row in csv.DictReader(file):
            base = np.array([float(row[axis]) for axis in "xyz"])
            for *rotation, shift in OPERATIONS:
                image = np.mod(np.array(rotation) @ base + np.array(shift), 1.0) * size
                if all(_nearest(image - atom.position).max() > 0.01 for atom in found):
                    found.append(Atom(row["atom"][0], int(row["electrons"]), image))
    return found


def _nearest(offset: np.ndarray) -> np.ndarray:
    size = np.array(CELL)
    return np.abs(offset - size * np.round(offset / size))


def density(members: list[Atom]) -> jax.Array:
    positions = jnp.asarray(np.stack([atom.position for atom in members]))
    signal = Torus.of(CELL, GRID).signal(PHYSICS.emitter, positions)
    weights = jnp.asarray([atom.electrons for atom in members], dtype=signal.dtype)
    values = signal @ weights
    return values / jnp.mean(values)


def errors(found: np.ndarray, members: list[Atom]) -> np.ndarray:
    """For each atom, the distance in angstrom to the nearest emitter."""
    truth = np.stack([atom.position for atom in members])
    offsets = truth[:, None, :] - found[None, :, :]
    offsets = offsets - np.array(CELL) * np.round(offsets / np.array(CELL))
    return np.sqrt(np.sum(offsets**2, axis=-1)).min(axis=1)


def read_electrons(
    torus: Torus, values: jax.Array, sites: np.ndarray
) -> tuple[np.ndarray, jax.Array]:
    """Fit a height per site; return the electrons and what the sites leave."""
    shapes = torus.signal(PHYSICS.emitter, jnp.asarray(sites))
    heights, *_ = jnp.linalg.lstsq(shapes, values)
    residual = jnp.clip(values - shapes @ heights, 0.0, None)
    electrons = np.asarray(heights) * OXYGEN_ELECTRONS / float(jnp.max(heights))
    return electrons, residual


def element_of(electrons: float) -> str:
    return {6: "C", 7: "N", 8: "O"}[int(np.clip(round(electrons), 6, 8))]


def density_frame(values: np.ndarray, emitters: np.ndarray) -> Image.Image:
    """The density seen along the c axis, with the emitters on top."""
    projected = values.reshape(GRID).max(axis=2)
    share = projected / projected.max()
    colours = PLASMA[np.clip(share * 255.0, 0.0, 255.0).astype(np.uint8)]
    image = Image.fromarray(colours, "RGB").resize(
        (MAP_SIZE, MAP_SIZE), Image.Resampling.BICUBIC
    )
    draw = ImageDraw.Draw(image)
    for x, y, _ in emitters:
        row, column = x / CELL[0] * MAP_SIZE, y / CELL[1] * MAP_SIZE
        box = (column - 7, row - 7, column + 7, row + 7)
        draw.ellipse(box, fill=EMITTER, outline="#ffffff", width=2)
    return image


def _gif(frames: list[Image.Image], duration: int) -> bytes:
    buffer = BytesIO()
    frames[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
    )
    return buffer.getvalue()


def main() -> None:
    members = atoms()
    heavy_atoms = [atom for atom in members if atom.element != "H"]
    light_atoms = [atom for atom in members if atom.element == "H"]
    values = density(members)
    torus = Torus.of(CELL, GRID, values.reshape(GRID))
    coverage = Coverage(torus, HardOcclusion(), PHYSICS)
    draws = torus.sample(jax.random.key(1), 32, HEAVY)
    random = float(np.mean([coverage.gain(draw) for draw in draws]))
    greedy = Greedy(torus, PHYSICS, Torus.of(CELL, CANDIDATES).points).place(HEAVY)
    steps: list[np.ndarray] = []

    def capture(step: Step) -> None:
        steps.append(np.asarray(step.positions))

    started = time.perf_counter()
    heavy = Descender(torus, PHYSICS, SEARCH, on_step=capture).run()
    sites = np.asarray(heavy.positions)
    electrons, residual = read_electrons(torus, values, sites)
    rest = Torus.of(CELL, GRID, residual.reshape(GRID))
    guess = Greedy(rest, PHYSICS, rest.points[::STRIDE]).place(LIGHT)
    light = Descender(
        rest,
        PHYSICS,
        DescentSettings(LIGHT, 400, report_every=50, step_size=0.005),
        start=guess[None],
    ).run()
    seconds = time.perf_counter() - started
    hydrogens = np.asarray(light.positions)
    heavy_error = errors(sites, heavy_atoms)
    light_error = errors(hydrogens, light_atoms)
    greedy_error = errors(np.asarray(greedy), heavy_atoms)
    print(f"gain random {random:.4f}, greedy {float(coverage.gain(greedy)):.4f}")
    print(f"gain descent {heavy.gain:.4f}, in {seconds:.0f}s")
    print(f"heavy worst {heavy_error.max():.3f} A")
    print(f"greedy worst {greedy_error.max():.3f} A")
    print(f"hydrogen worst {light_error.max():.3f} A")
    print("electrons", np.round(electrons, 2).tolist())
    labels = [element_of(float(count)) for count in electrons] + ["H"] * LIGHT
    found = np.concatenate([sites, np.mod(hydrogens, np.array(CELL))])
    view = AtomsImage(labels, found, CELL)
    (FIGURES / "case_urea.gif").write_bytes(
        _gif(
            [view.draw(360.0 * index / SPIN_FRAMES) for index in range(SPIN_FRAMES)],
            110,
        )
    )
    frames = [density_frame(np.asarray(values), step) for step in steps[::2]]
    (FIGURES / "layers_urea.gif").write_bytes(_gif(frames, 90))


if __name__ == "__main__":
    main()
