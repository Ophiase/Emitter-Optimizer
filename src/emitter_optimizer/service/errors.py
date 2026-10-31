from http import HTTPStatus


class ServiceError(Exception):
    """A request the service refuses, with the status to answer."""

    status = HTTPStatus.BAD_REQUEST

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class UnknownRoute(ServiceError):
    status = HTTPStatus.NOT_FOUND
