from fastapi import APIRouter, Depends, Request, Response

from app.api.v1.dto.dto_auth import LoginRequest, MeResponse
from app.api.v1.security import SESSION_COOKIE, get_bll_auth, get_current_actor
from app.bll.bll_auth import BllAuth
from app.core.config import settings
from app.entities.ent_user import EntActor

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=MeResponse)
def login(body: LoginRequest, response: Response, bll: BllAuth = Depends(get_bll_auth)) -> MeResponse:
    result = bll.login(body.badge, body.password)
    # Pas de durée sur le cookie : c'est le serveur qui décide de l'expiration
    # (15 minutes sans activité), et le cookie disparaît à la fermeture du navigateur.
    response.set_cookie(
        SESSION_COOKIE,
        result.token,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="strict",
        path="/",
    )
    return MeResponse.from_entity(result.user)


@router.post("/logout", status_code=204)
def logout(request: Request, bll: BllAuth = Depends(get_bll_auth)) -> Response:
    bll.logout(request.cookies.get(SESSION_COOKIE))
    response = Response(status_code=204)
    response.delete_cookie(SESSION_COOKIE, path="/", secure=settings.session_cookie_secure, samesite="strict")
    return response


@router.get("/me", response_model=MeResponse)
def me(actor: EntActor = Depends(get_current_actor), bll: BllAuth = Depends(get_bll_auth)) -> MeResponse:
    return MeResponse.from_entity(bll.current_user(actor))
