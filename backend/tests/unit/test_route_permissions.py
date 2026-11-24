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


CATALOGUE = set(Role) - {Role.TRAINER}
WRITERS = {Role.SECRETARY, Role.COORDINATOR, Role.SERVICE_HEAD, Role.IT_ADMIN}

EXPECTED = {
    ("POST", "/api/v1/users"): {Role.IT_ADMIN, Role.COORDINATOR},
    ("GET", "/api/v1/users"): {Role.IT_ADMIN, Role.COORDINATOR},
    ("GET", "/api/v1/users/by-badge/{badge}"): {Role.IT_ADMIN, Role.COORDINATOR},
    ("PUT", "/api/v1/users/{user_id}/roles"): {Role.IT_ADMIN},
    ("POST", "/api/v1/users/{user_id}/deactivate"): {Role.IT_ADMIN},
    ("POST", "/api/v1/users/{user_id}/reactivate"): {Role.IT_ADMIN},
    ("POST", "/api/v1/users/{user_id}/unblock"): {Role.IT_ADMIN},
    # La route ouvre à tous les lecteurs possibles ; la BLL vérifie le genre de fiche.
    ("GET", "/api/v1/history/{subject_type}/{subject_id}"): CATALOGUE,
    ("GET", "/api/v1/auth/me"): set(Role),
    ("GET", "/api/v1/domains"): CATALOGUE,
    ("POST", "/api/v1/domains"): {Role.IT_ADMIN},
    ("PUT", "/api/v1/domains/{domain_id}"): {Role.IT_ADMIN},
    ("POST", "/api/v1/domains/{domain_id}/subdomains"): {Role.IT_ADMIN},
    ("PUT", "/api/v1/subdomains/{subdomain_id}"): {Role.IT_ADMIN},
    ("GET", "/api/v1/trainings"): CATALOGUE,
    ("POST", "/api/v1/trainings"): WRITERS,
    ("GET", "/api/v1/trainings/{training_id}"): CATALOGUE,
    ("PUT", "/api/v1/trainings/{training_id}"): {Role.IT_ADMIN},
    ("GET", "/api/v1/trainers"): WRITERS,
    ("GET", "/api/v1/trainings/{training_id}/modules"): CATALOGUE,
    ("POST", "/api/v1/trainings/{training_id}/modules"): WRITERS,
    ("POST", "/api/v1/modules/{module_id}/trainer"): WRITERS,
    ("PUT", "/api/v1/modules/{module_id}"): {Role.IT_ADMIN},
    ("GET", "/api/v1/documents"): {Role.IT_ADMIN},
    ("GET", "/api/v1/trainings/{training_id}/documents"): CATALOGUE,
    ("POST", "/api/v1/modules/{module_id}/documents"): {Role.IT_ADMIN},
    ("POST", "/api/v1/documents/{document_id}/replace"): {Role.IT_ADMIN},
    ("GET", "/api/v1/documents/{document_id}/download"): {Role.TRAINER, Role.IT_ADMIN},
    ("GET", "/api/v1/me/modules"): {Role.TRAINER},
    ("GET", "/api/v1/training-requests"): CATALOGUE,
    ("POST", "/api/v1/training-requests"): WRITERS,
    ("GET", "/api/v1/training-requests/{request_id}"): CATALOGUE,
    ("PUT", "/api/v1/training-requests/{request_id}"): {Role.SECRETARY, Role.COORDINATOR, Role.IT_ADMIN},
    ("POST", "/api/v1/training-requests/{request_id}/decision"): {Role.COORDINATOR, Role.IT_ADMIN},
    ("GET", "/api/v1/training-sessions"): CATALOGUE,
    ("GET", "/api/v1/trainings/{training_id}/sessions"): CATALOGUE,
    ("GET", "/api/v1/training-requests/{request_id}/sessions"): CATALOGUE,
    ("GET", "/api/v1/training-sessions/{session_id}"): CATALOGUE,
    ("POST", "/api/v1/training-sessions"): {Role.COORDINATOR, Role.IT_ADMIN},
    ("PUT", "/api/v1/training-sessions/{session_id}/dates"): {Role.COORDINATOR, Role.IT_ADMIN},
    ("POST", "/api/v1/training-sessions/{session_id}/cancel"): {Role.COORDINATOR, Role.IT_ADMIN},
    ("POST", "/api/v1/training-sessions/{session_id}/restore"): {Role.IT_ADMIN},
}


def test_each_protected_route_allows_exactly_the_expected_roles() -> None:
    found = {(method, route.path): _declaration(route) for route in _routes() for method in route.methods}
    # Une route renommée ne doit pas sortir du contrôle sans bruit.
    missing = set(EXPECTED) - set(found)
    assert not missing, f"routes attendues introuvables : {sorted(missing)}"
    for key, roles in EXPECTED.items():
        assert found[key] == roles, key


@pytest.mark.parametrize("role", [Role.SECRETARY, Role.SERVICE_HEAD, Role.TRAINER, Role.DIRECTION])
def test_a_direct_call_from_a_role_without_the_right_is_refused(role: Role) -> None:
    app.dependency_overrides[get_current_actor] = lambda: actor(role)
    try:
        client = TestClient(app)
        some_id = "00000000-0000-0000-0000-000000000000"
        for method, path in [
            ("get", "/api/v1/users"),
            ("post", f"/api/v1/users/{some_id}/deactivate"),
            ("put", f"/api/v1/trainings/{some_id}"),
            ("post", "/api/v1/domains"),
        ]:
            response = client.request(method.upper(), path, json={} if method != "get" else None)
            assert response.status_code == 403, path
            assert response.json() == {"detail": "Votre rôle ne permet pas cette action."}
        # L'historique d'un compte : la route laisse passer, la BLL refuse.
        assert client.get(f"/api/v1/history/users/{some_id}").status_code == 403
    finally:
        app.dependency_overrides.clear()
