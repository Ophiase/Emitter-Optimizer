import uvicorn
from fastapi import APIRouter, FastAPI, Response

from emitter_optimizer.service.models import (
    Health,
    PlaceRequest,
    RunRequest,
    State,
    StopResult,
)
from emitter_optimizer.service.session import Session
from emitter_optimizer.service.settings import ServiceSettings

PNG_MEDIA_TYPE = "image/png"


class EmitterRouter:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.router = APIRouter(prefix="/api")
        self.router.get("/health", status_code=200)(self.health)
        self.router.get("/state", status_code=200)(self.state)
        self.router.get("/export", status_code=200)(self.state)
        self.router.get("/figure.png", status_code=200)(self.figure)
        self.router.post("/run", status_code=200)(self.run)
        self.router.post("/place", status_code=200)(self.place)
        self.router.post("/stop", status_code=200)(self.stop)

    def health(self) -> Health:
        return Health()

    def state(self) -> State:
        return self.session.state()

    def figure(self) -> Response:
        return Response(
            content=self.session.figure(),
            media_type=PNG_MEDIA_TYPE,
        )

    def run(self, request: RunRequest) -> State:
        return self.session.run(request)

    def place(self, request: PlaceRequest) -> State:
        return self.session.place(request)

    def stop(self) -> StopResult:
        return self.session.stop()


def create_app(session: Session) -> FastAPI:
    app = FastAPI(title="Emitter Optimizer")
    app.include_router(EmitterRouter(session).router)
    return app


def serve(session: Session, settings: ServiceSettings) -> None:
    uvicorn.run(
        create_app(session),
        host=str(settings.host),
        port=settings.port,
    )
