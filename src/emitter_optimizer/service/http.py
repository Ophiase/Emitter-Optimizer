"""The HTTP adapter: read a request, ask the router, write the answer."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from emitter_optimizer.service.router import EMPTY_BODY, Response, Router, routes_for
from emitter_optimizer.service.session import Session

HOST = "127.0.0.1"
PORT = 8765


class _SessionHandler(BaseHTTPRequestHandler):
    router: Router

    def do_GET(self) -> None:
        self._answer("GET")

    def do_POST(self) -> None:
        self._answer("POST")

    def log_message(self, format: str, *args: object) -> None:
        """Silence the access log: the router already answers every request."""
        del format, args

    def _answer(self, method: str) -> None:
        self._write(self.router.dispatch(method, self.path, self._body()))

    def _body(self) -> bytes:
        length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(length) if length else EMPTY_BODY

    def _write(self, response: Response) -> None:
        self.send_response(response.status)
        self.send_header("Content-Type", response.content_type)
        self.send_header("Content-Length", str(len(response.body)))
        self.end_headers()
        self.wfile.write(response.body)


def make_server(
    session: Session,
    host: str = HOST,
    port: int = PORT,
) -> ThreadingHTTPServer:
    class SessionHandler(_SessionHandler):
        pass

    SessionHandler.router = routes_for(session)
    return ThreadingHTTPServer((host, port), SessionHandler)


def serve(session: Session, host: str = HOST, port: int = PORT) -> None:
    server = make_server(session, host, port)
    bound_port = server.server_address[1]
    address = f"http://{host}:{bound_port}"  # hardcoded-url: the loopback address
    print(address, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
