"""Les routes du catalogue (US-010), avec un catalogue en mémoire."""

import pytest
from fastapi.testclient import TestClient

from app.api.v1.security import get_current_actor
from app.api.v1.trainings import get_bll_training
from app.bll.bll_training import BllTraining
from app.entities.ent_user import Role
from app.main import app
from tests.unit.fakes import FakeDalTraining, actor


@pytest.fixture
def dal() -> FakeDalTraining:
    return FakeDalTraining()


@pytest.fixture
def client(dal):
    app.dependency_overrides[get_bll_training] = lambda: BllTraining(dal)
    yield TestClient(app)
    app.dependency_overrides.clear()


def _as(role: Role) -> None:
    app.dependency_overrides[get_current_actor] = lambda: actor(role)


def test_the_catalogue_needs_a_connection(client) -> None:
    assert client.get("/api/v1/trainings").status_code == 401


def test_a_secretary_records_a_training_and_the_direction_reads_it(client, dal) -> None:
    _as(Role.SECRETARY)
    response = client.post(
        "/api/v1/trainings",
        json={"title": "Conduite sur la rampe", "subdomain_id": str(dal.subdomain_id("Conduite sur la rampe"))},
    )
    assert response.status_code == 201
    training_id = response.json()["id"]
    _as(Role.DIRECTION)
    body = client.get(f"/api/v1/trainings/{training_id}").json()
    assert body["domain_name"] == "Sûreté-Sécurité"
    assert [t["title"] for t in client.get("/api/v1/trainings").json()] == ["Conduite sur la rampe"]


def test_a_duplicate_title_answers_409_in_french(client, dal) -> None:
    _as(Role.SECRETARY)
    payload = {"title": "Protocole", "subdomain_id": str(dal.subdomain_id("Protocole"))}
    client.post("/api/v1/trainings", json=payload)
    response = client.post("/api/v1/trainings", json={**payload, "title": " protocole "})
    assert response.status_code == 409
    assert response.json() == {"detail": "Une formation porte déjà cet intitulé."}


def test_an_unknown_training_answers_404(client) -> None:
    _as(Role.SECRETARY)
    response = client.get("/api/v1/trainings/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_the_domains_come_with_their_subdomains(client) -> None:
    _as(Role.COORDINATOR)
    body = client.get("/api/v1/domains").json()
    assert [d["name"] for d in body] == ["Accueil", "Sûreté-Sécurité"]
    assert [s["name"] for s in body[0]["subdomains"]] == ["Civilité", "Protocole"]


def test_the_admin_adds_a_subdomain(client, dal) -> None:
    _as(Role.IT_ADMIN)
    response = client.post(f"/api/v1/domains/{dal.domain_id('Accueil')}/subdomains", json={"name": "Accueil VIP"})
    assert response.status_code == 201
    assert response.json()["name"] == "Accueil VIP"


def test_a_trainer_is_refused_the_catalogue(client) -> None:
    _as(Role.TRAINER)
    assert client.get("/api/v1/trainings").status_code == 403
    assert client.get("/api/v1/domains").status_code == 403
