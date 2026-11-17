import pytest
from fastapi.testclient import TestClient

from app.api.v1.security import SESSION_COOKIE, get_bll_auth
from app.api.v1.users import get_bll_user
from app.bll.bll_auth import BllAuth
from app.bll.bll_password import hash_password
from app.bll.bll_user import BllUser
from app.core.config import settings
from app.entities.ent_user import Role
from app.main import app
from tests.unit.fakes import FakeDalAuth, FakeDalUser, FakeEmail

PASSWORD = "formation2026"


@pytest.fixture
def world():
    users, auth = FakeDalUser(), FakeDalAuth()
    users.auth = auth
    admin = users.add_user_with_password("A01-01", hash_password(PASSWORD), roles=(Role.IT_ADMIN,))
    app.dependency_overrides[get_bll_auth] = lambda: BllAuth(dal_user=users, dal_auth=auth)
    app.dependency_overrides[get_bll_user] = lambda: BllUser(dal=users, email=FakeEmail())
    yield TestClient(app), users, admin
    app.dependency_overrides.clear()


def test_login_sets_a_protected_session_cookie(world, monkeypatch) -> None:
    client, *_ = world
    monkeypatch.setattr(settings, "session_cookie_secure", True)
    response = client.post("/api/v1/auth/login", json={"badge": "a01-01", "password": PASSWORD})

    assert response.status_code == 200
    assert response.json() == {"badge": "A01-01", "first_name": "Marie", "last_name": "Joseph", "roles": ["it_admin"]}
    cookie = response.headers["set-cookie"]
    assert cookie.startswith(f"{SESSION_COOKIE}=")
    for attribute in ("HttpOnly", "Secure", "SameSite=strict", "Path=/"):
        assert attribute in cookie
    assert "Max-Age" not in cookie and "expires" not in cookie.lower()


def test_wrong_credentials_are_401_with_the_generic_message(world) -> None:
    client, *_ = world
    response = client.post("/api/v1/auth/login", json={"badge": "A01-01", "password": "mauvais-mot-2"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Numéro de badge ou mot de passe incorrect."}
    assert "set-cookie" not in response.headers


def test_a_blocked_account_with_the_right_password_is_403(world) -> None:
    client, users, admin = world
    users.block(admin.id, None)
    response = client.post("/api/v1/auth/login", json={"badge": "A01-01", "password": PASSWORD})
    assert response.status_code == 403
    assert "bloqué" in response.json()["detail"]


def test_me_and_the_account_routes_work_once_logged_in(world) -> None:
    client, *_ = world
    assert client.get("/api/v1/auth/me").json() == {"detail": "Vous n'êtes pas connecté."}

    client.post("/api/v1/auth/login", json={"badge": "A01-01", "password": PASSWORD})
    assert client.get("/api/v1/auth/me").json()["badge"] == "A01-01"
    created = client.post(
        "/api/v1/users",
        json={"badge": "B07-42", "first_name": "Paul", "last_name": "Michel", "email": "p@example.test", "roles": ["trainer"]},
    )
    assert created.status_code == 201
    assert [u["badge"] for u in client.get("/api/v1/users").json()] == ["A01-01", "B07-42"]


def test_logout_closes_the_session_and_clears_the_cookie(world) -> None:
    client, *_ = world
    client.post("/api/v1/auth/login", json={"badge": "A01-01", "password": PASSWORD})
    token = client.cookies.get(SESSION_COOKIE)

    assert client.post("/api/v1/auth/logout").status_code == 204
    assert client.cookies.get(SESSION_COOKIE) is None
    client.cookies.set(SESSION_COOKIE, token)
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Votre session a expiré, reconnectez-vous."}


def test_the_admin_unblocks_through_the_api(world) -> None:
    client, users, _ = world
    blocked = users.add_user_with_password("B07-42", hash_password(PASSWORD))
    users.block(blocked.id, None)
    client.post("/api/v1/auth/login", json={"badge": "A01-01", "password": PASSWORD})

    response = client.post(f"/api/v1/users/{blocked.id}/unblock")
    assert response.status_code == 200
    assert response.json()["is_blocked"] is False
