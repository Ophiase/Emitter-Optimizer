import uvicorn
from fastapi import APIRouter, FastAPI, Response
from fastapi.responses import HTMLResponse

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
HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Emitter Optimizer</title>
  <style>
    :root { color-scheme: dark; }
    body { margin: 0; background: #0b0f14; color: #e8eef5;
      font: 16px/1.5 system-ui, sans-serif; }
    main { max-width: 1100px; margin: auto; padding: 1.5rem; }
    button { margin: 0 .5rem .75rem 0; padding: .5rem .9rem;
      border: 1px solid #2b3a4a; border-radius: .4rem;
      background: #14202c; color: inherit; cursor: pointer; }
    img, iframe { width: 100%; border: 1px solid #1f2b38;
      border-radius: .6rem; }
    iframe { height: 360px; margin-top: 1rem; }
  </style>
</head>
<body>
<main>
  <h1>Emitter Optimizer</h1>
  <p>Place emitters so the weighted, obstructed map they cover is maximized.</p>
  <button id="run">Run</button>
  <button id="stop">Stop</button>
  <button id="random">Place</button>
  <p id="state">loading...</p>
  <img id="map" alt="the value map" src="/api/figure.png">
  <iframe id="chart" src="/api/chart" title="the gain"></iframe>
</main>
<script>
const state = async () => {
  const value = await (await fetch('/api/state')).json();
  document.querySelector('#state').textContent =
    `gain ${value.gain.toFixed(4)} - ${value.emitters} emitters - ` +
    (value.running ? 'running' : 'idle');
  document.querySelector('#map').src = '/api/figure.png?t=' + Date.now();
};
document.querySelector('#run').onclick = async () => {
  await fetch('/api/run', {method: 'POST',
    headers: {'content-type': 'application/json'},
    body: JSON.stringify({iterations: 200})});
  await state();
};
document.querySelector('#stop').onclick = async () => {
  await fetch('/api/stop', {method: 'POST'});
  await state();
};
document.querySelector('#random').onclick = async () => {
  await fetch('/api/place', {method: 'POST',
    headers: {'content-type': 'application/json'},
    body: JSON.stringify({emitters: 15, seed: Date.now() % 1000})});
  await state();
};
state();
</script>
</body>
</html>
"""


class EmitterRouter:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.router = APIRouter(prefix="/api")
        self.router.get("/health", status_code=200)(self.health)
        self.router.get("/state", status_code=200)(self.state)
        self.router.get("/export", status_code=200)(self.state)
        self.router.get("/figure.png", status_code=200)(self.figure)
        self.router.get("/chart", status_code=200, response_class=HTMLResponse)(
            self.chart
        )
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

    def chart(self) -> HTMLResponse:
        return HTMLResponse(self.session.chart())

    def run(self, request: RunRequest) -> State:
        return self.session.run(request)

    def place(self, request: PlaceRequest) -> State:
        return self.session.place(request)

    def stop(self) -> StopResult:
        return self.session.stop()


def create_app(session: Session) -> FastAPI:
    app = FastAPI(title="Emitter Optimizer")
    app.include_router(EmitterRouter(session).router)

    @app.get("/", response_class=HTMLResponse)
    def index() -> HTMLResponse:
        return HTMLResponse(HTML)

    return app


def serve(session: Session, settings: ServiceSettings) -> None:
    uvicorn.run(
        create_app(session),
        host=str(settings.host),
        port=settings.port,
    )
