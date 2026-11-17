from fastapi import Depends, Request

from app.bll.bll_auth import BllAuth
from app.entities.ent_user import EntActor

# Le cookie de session (US-004 ; SOLUTION_DESIGN.md §7, ADR 5).
SESSION_COOKIE = "cfdc_session"


def get_bll_auth() -> BllAuth:
    return BllAuth()


def get_current_actor(request: Request, bll: BllAuth = Depends(get_bll_auth)) -> EntActor:
    """L'utilisateur connecté, lu dans le cookie de session ; chaque appel
    prolonge la session. Sans cookie : 401 « Vous n'êtes pas connecté. » ;
    session expirée ou fermée : 401 « Votre session a expiré… »."""
    return bll.authenticate(request.cookies.get(SESSION_COOKIE))
