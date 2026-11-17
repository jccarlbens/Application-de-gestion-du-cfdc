"""Qui peut appeler quoi (US-007).

Chaque route de l'API est **soit publique** (`Depends(public_route)`), **soit
protégée** par une liste de rôles (`Depends(require_roles(...))`), qui refuse
les autres en 403 avant tout traitement. Les règles plus fines (le
coordonnateur ne crée pas d'administrateur, le dernier administrateur est
protégé) restent dans la BLL. Un test (tests/unit/test_route_permissions.py)
échoue si une route n'est ni l'un ni l'autre.
"""

from collections.abc import Callable

from fastapi import Depends, Request

from app.bll.bll_auth import BllAuth
from app.core.exceptions import ForbiddenError
from app.entities.ent_user import EntActor, Role

# Le cookie de session (US-004 ; SOLUTION_DESIGN.md §7, ADR 5).
SESSION_COOKIE = "cfdc_session"

# Tous les rôles : il suffit d'être connecté.
ANY_ROLE = tuple(Role)


def get_bll_auth() -> BllAuth:
    return BllAuth()


def get_current_actor(request: Request, bll: BllAuth = Depends(get_bll_auth)) -> EntActor:
    """L'utilisateur connecté, lu dans le cookie de session ; chaque appel
    prolonge la session. Sans cookie : 401 « Vous n'êtes pas connecté. » ;
    session expirée ou fermée : 401 « Votre session a expiré… »."""
    return bll.authenticate(request.cookies.get(SESSION_COOKIE))


def public_route() -> None:
    """Marque une route ouverte exprès, sans connexion."""


def require_roles(*roles: Role) -> Callable[..., EntActor]:
    """La personne connectée, si l'un de ses rôles figure dans `roles` ;
    sinon 403, avant que la route ne fasse quoi que ce soit."""
    allowed = frozenset(roles)

    def check(actor: EntActor = Depends(get_current_actor)) -> EntActor:
        if not actor.roles & allowed:
            raise ForbiddenError("Votre rôle ne permet pas cette action.")
        return actor

    check.allowed_roles = allowed  # lu par le test de couverture des routes
    return check
