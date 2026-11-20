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


# --- Modules et formateurs (US-011) ----------------------------------------------


def _training_with_module(client, dal, trainer_id=None) -> tuple[str, str]:
    _as(Role.SECRETARY)
    training_id = client.post(
        "/api/v1/trainings", json={"title": "Rampe", "subdomain_id": str(dal.subdomain_id("Conduite sur la rampe"))}
    ).json()["id"]
    body = {"title": "Vitesses", "trainer_id": str(trainer_id) if trainer_id else None}
    module_id = client.post(f"/api/v1/trainings/{training_id}/modules", json=body).json()["id"]
    return training_id, module_id


def test_the_trainers_list_carries_no_personal_data(client, dal) -> None:
    dal.add_trainer("Paul", "Michel", "C03-15")
    _as(Role.SECRETARY)
    body = client.get("/api/v1/trainers").json()
    assert body == [
        {"id": body[0]["id"], "first_name": "Paul", "last_name": "Michel", "badge": "C03-15", "is_active": True, "is_trainer": True}
    ]


def test_a_secretary_adds_a_module_then_designates_its_trainer(client, dal) -> None:
    paul = dal.add_trainer("Paul", "Michel", "C03-15")
    training_id, module_id = _training_with_module(client, dal)
    response = client.post(f"/api/v1/modules/{module_id}/trainer", json={"trainer_id": str(paul.id)})
    assert response.status_code == 200
    _as(Role.DIRECTION)
    modules = client.get(f"/api/v1/trainings/{training_id}/modules").json()
    assert [(m["title"], m["trainer"]["badge"]) for m in modules] == [("Vitesses", "C03-15")]


def test_a_secretary_cannot_change_a_designated_trainer(client, dal) -> None:
    paul = dal.add_trainer("Paul", "Michel", "C03-15")
    rose = dal.add_trainer("Rose", "Pierre", "E05-55")
    _, module_id = _training_with_module(client, dal, trainer_id=paul.id)
    response = client.post(f"/api/v1/modules/{module_id}/trainer", json={"trainer_id": str(rose.id)})
    assert response.status_code == 403
    assert "seul l'administrateur" in response.json()["detail"]


def test_a_duplicate_module_title_answers_409(client, dal) -> None:
    training_id, _ = _training_with_module(client, dal)
    response = client.post(f"/api/v1/trainings/{training_id}/modules", json={"title": "vitesses "})
    assert response.status_code == 409
    assert response.json() == {"detail": "Cette formation a déjà un module de ce titre."}


def test_a_trainer_cannot_read_the_modules_of_a_training(client, dal) -> None:
    training_id, _ = _training_with_module(client, dal)
    _as(Role.TRAINER)
    assert client.get(f"/api/v1/trainings/{training_id}/modules").status_code == 403
