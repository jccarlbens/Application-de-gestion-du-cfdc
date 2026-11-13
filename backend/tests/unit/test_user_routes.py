import re

import pytest
from fastapi.testclient import TestClient

from app.api.v1.security import get_current_actor
from app.api.v1.users import get_bll_user
from app.bll.bll_user import BllUser
from app.entities.ent_user import Role
from app.main import app
from tests.unit.fakes import FakeDalUser, FakeEmail, actor

ACCOUNT = {
    "badge": "B07-42",
    "first_name": "Marie",
    "last_name": "Joseph",
    "email": "marie@example.test",
    "roles": ["secretary"],
}


@pytest.fixture
def email() -> FakeEmail:
    return FakeEmail()


@pytest.fixture
def client(email):
    bll = BllUser(dal=FakeDalUser(), email=email)
    app.dependency_overrides[get_bll_user] = lambda: bll
    yield TestClient(app)
    app.dependency_overrides.clear()


def _as(*roles: Role) -> None:
    app.dependency_overrides[get_current_actor] = lambda: actor(*roles)


def test_every_account_route_refuses_when_nobody_is_connected(client) -> None:
    some_id = "00000000-0000-0000-0000-000000000000"
    for method, path in [
        ("post", "/api/v1/users"),
        ("get", "/api/v1/users"),
        ("put", f"/api/v1/users/{some_id}/roles"),
        ("post", f"/api/v1/users/{some_id}/deactivate"),
        ("post", f"/api/v1/users/{some_id}/reactivate"),
    ]:
        body = {"roles": ["trainer"]} if method == "put" else ACCOUNT
        response = client.get(path) if method == "get" else getattr(client, method)(path, json=body)
        assert response.status_code == 401, path
        assert response.json() == {"detail": "Vous n'êtes pas connecté."}


def test_admin_creates_lists_and_manages_an_account(client, email) -> None:
    _as(Role.IT_ADMIN)
    created = client.post("/api/v1/users", json=ACCOUNT)
    assert created.status_code == 201
    body = created.json()
    assert body["badge"] == "B07-42" and body["roles"] == ["secretary"] and body["has_password"] is False
    assert "password_hash" not in body
    assert len(email.sent) == 1

    assert [u["badge"] for u in client.get("/api/v1/users").json()] == ["B07-42"]
    user_id = body["id"]
    assert client.put(f"/api/v1/users/{user_id}/roles", json={"roles": ["trainer", "direction"]}).json()["roles"] == [
        "direction",
        "trainer",
    ]
    assert client.post(f"/api/v1/users/{user_id}/deactivate").json()["is_active"] is False
    assert client.post(f"/api/v1/users/{user_id}/reactivate").json()["is_active"] is True


def test_secretary_is_forbidden_with_a_french_message(client) -> None:
    _as(Role.SECRETARY)
    response = client.post("/api/v1/users", json=ACCOUNT)
    assert response.status_code == 403
    assert "créent des comptes" in response.json()["detail"]


def test_coordinator_cannot_grant_the_admin_role(client) -> None:
    _as(Role.COORDINATOR)
    response = client.post("/api/v1/users", json={**ACCOUNT, "roles": ["it_admin"]})
    assert response.status_code == 403


def test_input_errors_come_back_in_french(client) -> None:
    _as(Role.IT_ADMIN)
    assert client.post("/api/v1/users", json={**ACCOUNT, "badge": "XX"}).status_code == 422
    client.post("/api/v1/users", json=ACCOUNT)
    duplicate = client.post("/api/v1/users", json={**ACCOUNT, "email": "autre@example.test"})
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Ce numéro de badge est déjà utilisé."


def test_unknown_account_is_404(client) -> None:
    _as(Role.IT_ADMIN)
    response = client.post("/api/v1/users/00000000-0000-0000-0000-000000000000/deactivate")
    assert response.status_code == 404


def test_the_password_link_works_without_being_connected(client, email) -> None:
    _as(Role.IT_ADMIN)
    client.post("/api/v1/users", json=ACCOUNT)
    app.dependency_overrides.pop(get_current_actor)
    token = re.search(r"jeton=([\w-]+)", email.sent[0]["body"]).group(1)

    assert client.post("/api/v1/password/setup", json={"token": token, "password": "court"}).status_code == 422
    assert client.post("/api/v1/password/setup", json={"token": token, "password": "formation2026"}).status_code == 204
    reused = client.post("/api/v1/password/setup", json={"token": token, "password": "formation2026"})
    assert reused.status_code == 410
    assert "plus valable" in reused.json()["detail"]
