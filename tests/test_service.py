import json
import threading
from http.client import HTTPConnection
from typing import Any

from emitter_optimizer.service import Session, make_server


class Service:
    def __init__(self) -> None:
        self.session = Session(map_scale=(10.0, 10.0), grid_size=(4, 4), emitters=2)
        self.server = make_server(self.session, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.port = int(self.server.server_address[1])

    def __enter__(self) -> Service:
        self.thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.server.shutdown()
        self.server.server_close()

    def get(self, path: str) -> bytes:
        connection = HTTPConnection("127.0.0.1", self.port, timeout=10)
        connection.request("GET", path)
        payload = connection.getresponse().read()
        connection.close()
        return payload

    def post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        connection = HTTPConnection("127.0.0.1", self.port, timeout=10)
        connection.request(
            "POST",
            path,
            body=json.dumps(body),
            headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        payload = json.loads(response.read())
        connection.close()
        return payload


def test_the_service_answers_state_run_place_and_a_figure() -> None:
    with Service() as service:
        state = json.loads(service.get("/api/state"))
        assert state["emitters"] == 2
        assert len(state["positions"]) == 2

        run = service.post("/api/run", {"iterations": 2, "seed": 0})
        assert len(run["history"]) == 2

        placed = service.post(
            "/api/place",
            {"positions": [[1.0, 2.0], [3.0, 4.0]]},
        )
        assert placed["positions"] == [[1.0, 2.0], [3.0, 4.0]]

        assert service.get("/api/figure.png").startswith(b"\x89PNG")
        assert json.loads(service.get("/api/health")) == {"ok": True}


def test_a_seed_reproduces_the_same_positions() -> None:
    with Service() as service:
        first = service.post("/api/run", {"iterations": 2, "seed": 7})
        second = service.post("/api/run", {"iterations": 2, "seed": 7})

        assert first["positions"] == second["positions"]


def test_a_bad_request_is_an_answer_not_a_crash() -> None:
    with Service() as service:
        answer = service.post("/api/place", {"positions": [[1.0]]})

        assert "error" in answer
