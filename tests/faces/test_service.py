from fastapi.testclient import TestClient

from emitter_optimizer.service import Session, create_app


def make_client() -> TestClient:
    session = Session(map_scale=(10.0, 10.0), grid_size=(4, 4), emitters=2)
    return TestClient(create_app(session))


def test_state_run_place_and_a_figure() -> None:
    client = make_client()

    state = client.get("/api/state").json()
    assert state["emitters"] == 2
    assert len(state["positions"]) == 2

    run = client.post("/api/run", json={"iterations": 2, "seed": 0}).json()
    assert len(run["history"]) == 2

    placed = client.post(
        "/api/place",
        json={"positions": [[1.0, 2.0], [3.0, 4.0]]},
    ).json()
    assert placed["positions"] == [[1.0, 2.0], [3.0, 4.0]]

    assert client.get("/api/figure.png").content.startswith(b"\x89PNG")
    assert client.get("/api/health").json() == {"ok": True}


def test_a_seed_reproduces_the_same_positions() -> None:
    client = make_client()

    first = client.post("/api/run", json={"iterations": 2, "seed": 7}).json()
    second = client.post("/api/run", json={"iterations": 2, "seed": 7}).json()

    assert first["positions"] == second["positions"]


def test_a_bad_body_and_an_unknown_route_are_answers() -> None:
    client = make_client()

    assert client.post("/api/place", json={"positions": [[1.0]]}).status_code == 422
    assert client.get("/api/nope").status_code == 404
