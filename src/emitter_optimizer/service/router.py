"""The routes of the service, and the mapping from an error to an answer."""

import json
from collections.abc import Callable
from dataclasses import dataclass
from http import HTTPStatus

from pydantic import BaseModel, ValidationError

from emitter_optimizer.service.errors import ServiceError
from emitter_optimizer.service.models import Health, PlaceRequest, RunRequest
from emitter_optimizer.service.session import Session

JSON = "application/json"
PNG = "image/png"
EMPTY_BODY = b"{}"
Route = Callable[[bytes], "Response"]


@dataclass(frozen=True)
class Response:
    """A status, a content type and a body: what the transport has to write."""

    status: HTTPStatus
    content_type: str
    body: bytes

    @classmethod
    def json(cls, payload: BaseModel, status: HTTPStatus = HTTPStatus.OK) -> Response:
        return cls(status, JSON, payload.model_dump_json().encode("utf-8"))

    @classmethod
    def png(cls, payload: bytes) -> Response:
        return cls(HTTPStatus.OK, PNG, payload)

    @classmethod
    def error(cls, message: str, status: HTTPStatus) -> Response:
        body = json.dumps({"error": message}).encode("utf-8")
        return cls(status, JSON, body)


class Router:
    """A method and a path to one handler; an unknown route is an answer."""

    def __init__(self) -> None:
        self._routes: dict[tuple[str, str], Route] = {}

    def add(self, method: str, path: str, route: Route) -> None:
        self._routes[method, path] = route

    def dispatch(self, method: str, path: str, body: bytes) -> Response:
        route = self._routes.get((method, path))
        if route is None:
            return Response.error(f"no route {method} {path}", HTTPStatus.NOT_FOUND)
        try:
            return route(body)
        except ValidationError as error:
            return Response.error(error.json(), HTTPStatus.UNPROCESSABLE_ENTITY)
        except ServiceError as error:
            return Response.error(error.message, error.status)


def routes_for(session: Session) -> Router:
    """Every route of the service, bound to one session."""
    router = Router()
    router.add("GET", "/api/health", lambda _: Response.json(Health()))
    router.add("GET", "/api/state", lambda _: Response.json(session.state()))
    router.add("GET", "/api/export", lambda _: Response.json(session.state()))
    router.add("GET", "/api/figure.png", lambda _: Response.png(session.figure()))
    router.add(
        "POST",
        "/api/run",
        lambda body: Response.json(session.run(RunRequest.model_validate_json(body))),
    )
    router.add(
        "POST",
        "/api/place",
        lambda body: Response.json(
            session.place(PlaceRequest.model_validate_json(body))
        ),
    )
    router.add("POST", "/api/stop", lambda _: Response.json(session.stop()))
    return router
