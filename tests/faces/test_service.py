import jax.numpy as jnp
from fastapi.testclient import TestClient

from emitter_optimizer.kernel import Extent, GridShape, Physics, Scene
from emitter_optimizer.service import Session, create_app
from emitter_optimizer.service.models import RunRequest


def make_client() -> TestClient:
    scene = Scene.of(Extent(10.0, 10.0), GridShape(4, 4))
    physics = Physics(
        emitter=lambda distance: jnp.exp(-distance / 5.0),
        sensor=lambda signal: signal,
    )
    session = Session(scene, physics, emitters=2)
    return TestClient(create_app(session))


def test_state_run_place_and_a_figure() -> None:
    client = make_client()

    state = client.get("/api/state").json()
    assert state["emitters"] == 2
    assert len(state["positions"]) == 2

    run = client.post("/api/run", json={"iterations": 2, "seed": 0}).json()
    assert len(run["history"]) == 2

    placed = client.post(
        "/api/place", json={"positions": [[1.0, 2.0], [3.0, 4.0]]}
    ).json()
    assert placed["positions"] == [[1.0, 2.0], [3.0, 4.0]]

    assert client.get("/api/figure.png").content.startswith(b"\x89PNG")
    assert client.get("/api/health").json() == {"ok": True}


def test_the_page_and_the_chart_are_served() -> None:
    client = make_client()

    assert "Emitter Optimizer" in client.get("/").text
    assert "plotly" in client.get("/api/chart").text.lower()


def test_a_seed_reproduces_the_same_positions() -> None:
    client = make_client()

    first = client.post("/api/run", json={"iterations": 2, "seed": 7}).json()
    second = client.post("/api/run", json={"iterations": 2, "seed": 7}).json()

    assert first["positions"] == second["positions"]


def test_a_relocation_never_ends_below_the_descent_alone() -> None:
    density = jnp.zeros((8, 8)).at[1, 1].set(1.0).at[6, 6].set(1.0)
    scene = Scene.of(Extent(10.0, 10.0), GridShape(8, 8), density)
    physics = Physics(
        emitter=lambda distance: jnp.exp(-distance),
        sensor=lambda signal: 1.0 - jnp.exp(-signal),
    )
    alone = Session(scene, physics, emitters=2).run(RunRequest(iterations=4, seed=0))
    relocated = Session(scene, physics, emitters=2).run(
        RunRequest(iterations=4, seed=0, relocate=True)
    )

    assert relocated.gain >= alone.gain


def test_a_bad_body_and_an_unknown_route_are_answers() -> None:
    client = make_client()

    assert client.post("/api/place", json={"positions": [[1.0]]}).status_code == 422
    assert client.get("/api/nope").status_code == 404
