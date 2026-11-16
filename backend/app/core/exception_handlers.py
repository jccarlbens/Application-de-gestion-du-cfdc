from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppError,
    DuplicateBadgeError,
    DuplicateEmailError,
    EmailDeliveryError,
    ForbiddenError,
    InvalidInputError,
    InvalidPasswordLinkError,
    LastAdminError,
    NotAuthenticatedError,
    UserNotFoundError,
    WeakPasswordError,
)

# Le SEUL endroit qui traduit une exception de domaine en réponse HTTP : les
# routeurs de api/ ne font jamais de try/except pour cela. Le message de
# l'exception est affiché tel quel à l'utilisateur : il est en français.
_STATUS = {
    NotAuthenticatedError: 401,
    ForbiddenError: 403,
    UserNotFoundError: 404,
    DuplicateBadgeError: 409,
    DuplicateEmailError: 409,
    LastAdminError: 409,
    InvalidInputError: 422,
    WeakPasswordError: 422,
    InvalidPasswordLinkError: 410,
    EmailDeliveryError: 502,
}


def register_exception_handlers(app: FastAPI) -> None:
    for error, status in _STATUS.items():
        app.add_exception_handler(error, _handler(status))


def _handler(status: int):
    async def handle(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=status, content={"detail": str(exc)})

    return handle
