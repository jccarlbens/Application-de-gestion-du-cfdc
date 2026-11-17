"""Chaque route de l'API est soit publique, soit protégée par une liste de
rôles (US-007). Une route oubliée fait échouer ce test : elle ne passe pas
inaperçue, comme une table oubliée par le journal (US-003)."""

import pytest
from fastapi.testclient import TestClient

from app.api.v1.security import get_current_actor, public_route
from app.entities.ent_user import Role
from app.main import app
from tests.unit.api_routes import ApiRoute, api_routes
from tests.unit.fakes import actor

PUBLIC = {
    ("GET", "/api/v1/health"),
    ("POST", "/api/v1/auth/login"),
    ("POST", "/api/v1/auth/logout"),
    ("POST", "/api/v1/password/setup"),
}


def _calls(dependant) -> list:
    found = [dependant.call]
    for sub in dependant.dependencies:
        found.extend(_calls(sub))
    return found


def _routes() -> list[ApiRoute]:
    return api_routes()


def _declaration(route: ApiRoute):
    calls = _calls(route.dependant)
    if public_route in calls:
        return "public"
    guards = [c for c in calls if hasattr(c, "allowed_roles")]
    return guards[0].allowed_roles if guards else None


def test_finds_the_routes_it_must_watch() -> None:
    assert len(_routes()) >= 10


@pytest.mark.parametrize("route", _routes(), ids=lambda r: f"{sorted(r.methods)[0]} {r.path}")
def test_every_route_is_public_or_protected(route: ApiRoute) -> None:
    declaration = _declaration(route)
    assert declaration is not None, f"{route.path} n'est ni publique ni protégée par require_roles"
    for method in route.methods:
        is_public = (method, route.path) in PUBLIC
        assert (declaration == "public") == is_public, f"{method} {route.path} : {declaration}"


def test_admin_only_routes_are_admin_only() -> None:
    expected = {
        "/api/v1/users": {Role.IT_ADMIN, Role.COORDINATOR},
        "/api/v1/users/{user_id}/roles": {Role.IT_ADMIN},
        "/api/v1/users/{user_id}/deactivate": {Role.IT_ADMIN},
        "/api/v1/users/{user_id}/reactivate": {Role.IT_ADMIN},
        "/api/v1/users/{user_id}/unblock": {Role.IT_ADMIN},
        "/api/v1/history/users/{user_id}": {Role.IT_ADMIN, Role.COORDINATOR},
        "/api/v1/auth/me": set(Role),
    }
    for route in _routes():
        if route.path in expected:
            assert _declaration(route) == expected[route.path], route.path


@pytest.mark.parametrize("role", [Role.SECRETARY, Role.SERVICE_HEAD, Role.TRAINER, Role.DIRECTION])
def test_a_direct_call_from_a_role_without_the_right_is_refused(role: Role) -> None:
    app.dependency_overrides[get_current_actor] = lambda: actor(role)
    try:
        client = TestClient(app)
        some_id = "00000000-0000-0000-0000-000000000000"
        for method, path in [
            ("get", "/api/v1/users"),
            ("post", f"/api/v1/users/{some_id}/deactivate"),
            ("get", f"/api/v1/history/users/{some_id}"),
        ]:
            response = getattr(client, method)(path)
            assert response.status_code == 403, path
            assert response.json() == {"detail": "Votre rôle ne permet pas cette action."}
    finally:
        app.dependency_overrides.clear()
