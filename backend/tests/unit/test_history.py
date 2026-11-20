import uuid
from dataclasses import replace
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.api.v1.history import get_bll_history
from app.api.v1.security import get_current_actor
from app.bll import bll_history
from app.bll.bll_history import BllHistory
from app.core.exceptions import ForbiddenError, RecordNotFoundError
from app.entities.ent_audit import MASKED, AuditAction, EntAuditEntry
from app.entities.ent_user import Role
from app.main import app
from tests.unit.api_routes import api_routes
from tests.unit.fakes import actor

USER_ID = str(uuid.uuid4())


def _entry(after: dict) -> EntAuditEntry:
    return EntAuditEntry(
        occurred_at=datetime(2026, 11, 16, tzinfo=UTC),
        actor_user_id=None,
        actor_label="Ligne de commande (administrateur)",
        subject_type="users",
        subject_id=USER_ID,
        table_name="users",
        action=AuditAction.CREATE,
        before=None,
        after=after,
    )


class _FakeDalAudit:
    def __init__(self, entries) -> None:
        self.entries = entries

    def history(self, subject_type, subject_id):
        return [e for e in self.entries if e.subject_type == subject_type and e.subject_id == subject_id]


@pytest.mark.parametrize("role", [Role.IT_ADMIN, Role.COORDINATOR])
def test_admin_and_coordinator_read_an_account_history(role) -> None:
    bll = BllHistory(_FakeDalAudit([_entry({"badge": "B07-42"})]))
    assert bll.history(actor(role), "users", USER_ID)[0].after == {"badge": "B07-42"}


@pytest.mark.parametrize("role", [Role.SECRETARY, Role.SERVICE_HEAD, Role.TRAINER, Role.DIRECTION])
def test_other_roles_cannot_read_an_account_history(role) -> None:
    with pytest.raises(ForbiddenError):
        BllHistory(_FakeDalAudit([])).history(actor(role), "users", USER_ID)


def test_an_unknown_kind_of_record_has_no_history() -> None:
    with pytest.raises(RecordNotFoundError):
        BllHistory(_FakeDalAudit([])).history(actor(Role.IT_ADMIN), "nothing", USER_ID)


def test_personal_fields_are_masked_for_roles_that_do_not_see_them(monkeypatch) -> None:
    # Les participants (Epic 4) auront des champs personnels ; le masquage est déjà prêt.
    monkeypatch.setitem(bll_history._READERS, "users", frozenset({Role.SECRETARY, Role.IT_ADMIN}))
    monkeypatch.setattr(bll_history, "personal_fields", lambda table: frozenset({"phone"}))
    bll = BllHistory(_FakeDalAudit([_entry({"badge": "B07-42", "phone": "+509 3700 0000", "fax": None})]))

    assert bll.history(actor(Role.SECRETARY), "users", USER_ID)[0].after == {
        "badge": "B07-42",
        "phone": MASKED,
        "fax": None,
    }
    assert bll.history(actor(Role.IT_ADMIN), "users", USER_ID)[0].after["phone"] == "+509 3700 0000"


@pytest.fixture
def client():
    app.dependency_overrides[get_bll_history] = lambda: BllHistory(_FakeDalAudit([_entry({"badge": "B07-42"})]))
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_the_history_route_needs_a_connection(client) -> None:
    response = client.get(f"/api/v1/history/users/{USER_ID}")
    assert response.status_code == 401


def test_the_history_route_answers_the_admin(client) -> None:
    app.dependency_overrides[get_current_actor] = lambda: actor(Role.IT_ADMIN)
    body = client.get(f"/api/v1/history/users/{USER_ID}").json()
    assert body[0]["action"] == "create"
    assert body[0]["actor_label"] == "Ligne de commande (administrateur)"
    assert body[0]["after"] == {"badge": "B07-42"}


def test_the_history_route_refuses_a_trainer(client) -> None:
    app.dependency_overrides[get_current_actor] = lambda: actor(Role.TRAINER)
    assert client.get(f"/api/v1/history/users/{USER_ID}").status_code == 403


def test_no_route_writes_to_the_journal() -> None:
    history = [r for r in api_routes() if r.path.startswith("/api/v1/history")]
    assert history, "aucune route d'historique trouvée : le test ne vérifierait rien"
    assert all(r.methods <= {"GET", "HEAD"} for r in history)


@pytest.mark.parametrize("kind", ["trainings", "domains", "subdomains"])
@pytest.mark.parametrize("role", [Role.SECRETARY, Role.COORDINATOR, Role.SERVICE_HEAD, Role.IT_ADMIN, Role.DIRECTION])
def test_everyone_who_sees_the_catalogue_reads_its_history(kind, role) -> None:
    entry = replace(_entry({"title": "Protocole"}), subject_type=kind)
    assert BllHistory(_FakeDalAudit([entry])).history(actor(role), kind, USER_ID)[0].after == {"title": "Protocole"}


@pytest.mark.parametrize("kind", ["trainings", "domains", "subdomains"])
def test_trainers_do_not_read_the_catalogue_history(kind) -> None:
    with pytest.raises(ForbiddenError):
        BllHistory(_FakeDalAudit([])).history(actor(Role.TRAINER), kind, USER_ID)


def test_the_route_gives_the_author_name_to_a_secretary() -> None:
    entry = replace(_entry({"title": "Protocole"}), subject_type="trainings", actor_name="Ada Admin (Z01-01)")
    app.dependency_overrides[get_bll_history] = lambda: BllHistory(_FakeDalAudit([entry]))
    app.dependency_overrides[get_current_actor] = lambda: actor(Role.SECRETARY)
    try:
        body = TestClient(app).get(f"/api/v1/history/trainings/{USER_ID}").json()
    finally:
        app.dependency_overrides.clear()
    assert body[0]["actor_name"] == "Ada Admin (Z01-01)"


def test_an_unknown_kind_answers_404() -> None:
    app.dependency_overrides[get_current_actor] = lambda: actor(Role.IT_ADMIN)
    try:
        response = TestClient(app).get(f"/api/v1/history/nothing/{USER_ID}")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 404
