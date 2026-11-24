"""Les règles des sessions de formation (US-015)."""

import uuid
from dataclasses import replace
from datetime import UTC, date, datetime

import pytest
from fastapi.testclient import TestClient

from app.api.v1.security import get_current_actor
from app.api.v1.training_sessions import get_bll_training_session
from app.bll.bll_training_session import BllTrainingSession
from app.core.exceptions import ForbiddenError, InvalidInputError, RecordNotFoundError
from app.entities.ent_training_request import RequestStatus
from app.entities.ent_training_session import EntTrainingSession, SessionStatus
from app.entities.ent_user import Role
from app.main import app
from tests.unit.fakes import actor

TODAY = date(2026, 11, 24)
TRAINING, OTHER = uuid.uuid4(), uuid.uuid4()


class FakeTrainings:
    def training_exists(self, training_id) -> bool:
        return training_id in (TRAINING, OTHER)


class FakeRequests:
    def __init__(self) -> None:
        self.rows = {}

    def add(self, status: RequestStatus):
        row = type("R", (), {"id": uuid.uuid4(), "status": status, "training_id": TRAINING})()
        self.rows[row.id] = row
        return row

    def get(self, request_id):
        if request_id not in self.rows:
            raise RecordNotFoundError("Cette demande de formation n'existe pas.")
        return self.rows[request_id]


class FakeDal:
    def __init__(self) -> None:
        self.rows: dict[uuid.UUID, EntTrainingSession] = {}

    def list(self, training_id=None, request_id=None):
        rows = [r for r in self.rows.values() if (training_id is None or r.training_id == training_id) and (request_id is None or r.request_id == request_id)]
        return sorted(rows, key=lambda r: r.starts_on)

    def get(self, session_id):
        if session_id not in self.rows:
            raise RecordNotFoundError("Cette session de formation n'existe pas.")
        return self.rows[session_id]

    def create(self, training_id, request_id, label, starts_on, ends_on, planned_by):
        row = EntTrainingSession(uuid.uuid4(), training_id, "Rampe", request_id, None, label, starts_on, ends_on,
                                 SessionStatus.PLANNED, None, "X", datetime(2026, 11, 24, tzinfo=UTC))
        self.rows[row.id] = row
        return row

    def update(self, session_id, **changes):
        if "status" in changes:
            changes["status"] = SessionStatus(changes["status"])
        self.rows[session_id] = replace(self.rows[session_id], **changes)
        return self.rows[session_id]


@pytest.fixture
def requests():
    return FakeRequests()


@pytest.fixture
def bll(requests):
    return BllTrainingSession(FakeDal(), FakeTrainings(), requests, today=lambda: TODAY)


def _plan(bll, who=Role.COORDINATOR, start=date(2026, 12, 2), end=date(2026, 12, 5), **kw):
    return bll.plan(actor(who), kw.get("training_id", TRAINING), kw.get("request_id"), kw.get("label"), start, end)


@pytest.mark.parametrize("role", [Role.COORDINATOR, Role.IT_ADMIN])
def test_coordinator_and_admin_plan(bll, role) -> None:
    session = _plan(bll, who=role, label="  Groupe   A ")
    assert (session.status, session.label) == (SessionStatus.PLANNED, "Groupe A")


@pytest.mark.parametrize("role", [Role.SECRETARY, Role.SERVICE_HEAD, Role.DIRECTION, Role.TRAINER])
def test_others_do_not_plan(bll, role) -> None:
    with pytest.raises(ForbiddenError):
        _plan(bll, who=role)


def test_no_maximum_duration_and_past_dates_are_allowed(bll) -> None:
    assert _plan(bll, start=date(2026, 1, 5), end=date(2026, 3, 27)).ends_on == date(2026, 3, 27)
    assert _plan(bll, start=date(2026, 12, 2), end=date(2026, 12, 2)).starts_on == date(2026, 12, 2)


@pytest.mark.parametrize(("start", "end", "message"), [(date(2026, 12, 5), date(2026, 12, 2), "précéder"), (None, date(2026, 12, 2), "obligatoires")])
def test_dates_are_checked_in_french(bll, start, end, message) -> None:
    with pytest.raises(InvalidInputError, match=message):
        _plan(bll, start=start, end=end)


def test_a_session_only_answers_an_approved_request_and_takes_its_training(bll, requests) -> None:
    approved = requests.add(RequestStatus.APPROVED)
    session = _plan(bll, training_id=None, request_id=approved.id)
    assert (session.training_id, session.request_id) == (TRAINING, approved.id)
    for status in (RequestStatus.PENDING, RequestStatus.REFUSED):
        with pytest.raises(InvalidInputError, match="demande validée"):
            _plan(bll, training_id=None, request_id=requests.add(status).id)
    with pytest.raises(InvalidInputError, match="formation de cette demande"):
        _plan(bll, training_id=OTHER, request_id=approved.id)


def test_an_unknown_training_is_refused(bll) -> None:
    with pytest.raises(InvalidInputError, match="formation du catalogue"):
        _plan(bll, training_id=uuid.uuid4())


def test_reschedule_a_planned_session(bll) -> None:
    session = _plan(bll)
    moved = bll.reschedule(actor(Role.COORDINATOR), session.id, date(2026, 12, 9), date(2026, 12, 12))
    assert (moved.starts_on, moved.ends_on) == (date(2026, 12, 9), date(2026, 12, 12))


def test_a_finished_session_is_moved_by_the_admin_only(bll) -> None:
    finished = _plan(bll, start=date(2026, 11, 2), end=date(2026, 11, 6))
    assert finished.display_status(TODAY) == "finished"
    with pytest.raises(ForbiddenError, match="terminée"):
        bll.reschedule(actor(Role.COORDINATOR), finished.id, date(2026, 11, 3), date(2026, 11, 7))
    assert bll.reschedule(actor(Role.IT_ADMIN), finished.id, date(2026, 11, 3), date(2026, 11, 7)).ends_on == date(2026, 11, 7)


def test_a_session_ending_today_is_not_finished(bll) -> None:
    assert _plan(bll, start=date(2026, 11, 20), end=TODAY).display_status(TODAY) == "planned"


def test_cancel_needs_a_reason_and_is_final_except_for_the_admin(bll) -> None:
    session = _plan(bll)
    with pytest.raises(InvalidInputError, match="motif"):
        bll.cancel(actor(Role.COORDINATOR), session.id, "  ")
    cancelled = bll.cancel(actor(Role.COORDINATOR), session.id, " Formateur absent ")
    assert (cancelled.status, cancelled.cancel_reason, cancelled.display_status(TODAY)) == (SessionStatus.CANCELLED, "Formateur absent", "cancelled")
    with pytest.raises(InvalidInputError, match="déjà annulée"):
        bll.cancel(actor(Role.COORDINATOR), session.id, "x")
    with pytest.raises(InvalidInputError, match="annulée"):
        bll.reschedule(actor(Role.COORDINATOR), session.id, date(2026, 12, 9), date(2026, 12, 9))
    with pytest.raises(ForbiddenError):
        bll.restore(actor(Role.COORDINATOR), session.id)
    restored = bll.restore(actor(Role.IT_ADMIN), session.id)
    assert (restored.status, restored.cancel_reason) == (SessionStatus.PLANNED, None)
    with pytest.raises(InvalidInputError, match="pas annulée"):
        bll.restore(actor(Role.IT_ADMIN), session.id)


def test_listing_puts_coming_sessions_first_and_trainers_do_not_see(bll) -> None:
    past_old = _plan(bll, start=date(2026, 3, 2), end=date(2026, 3, 3))
    past_recent = _plan(bll, start=date(2026, 10, 1), end=date(2026, 10, 2))
    soon = _plan(bll, start=date(2026, 11, 30), end=date(2026, 12, 1))
    later = _plan(bll, start=date(2027, 1, 4), end=date(2027, 1, 8))
    assert [s.id for s in bll.list(actor(Role.SECRETARY))] == [soon.id, later.id, past_recent.id, past_old.id]
    with pytest.raises(ForbiddenError):
        bll.list(actor(Role.TRAINER))


def test_routes_show_the_deduced_status() -> None:
    bll = BllTrainingSession(FakeDal(), FakeTrainings(), FakeRequests(), today=lambda: TODAY)
    app.dependency_overrides[get_bll_training_session] = lambda: bll
    app.dependency_overrides[get_current_actor] = lambda: actor(Role.COORDINATOR)
    try:
        client = TestClient(app)
        body = {"training_id": str(TRAINING), "starts_on": "2026-11-02", "ends_on": "2026-11-06"}
        created = client.post("/api/v1/training-sessions", json=body)
        assert created.status_code == 201 and created.json()["status"] == "finished"
        bad = client.post("/api/v1/training-sessions", json={**body, "ends_on": "2026-11-01"})
        assert bad.status_code == 422 and "précéder" in bad.json()["detail"]
        assert client.post(f"/api/v1/training-sessions/{created.json()['id']}/restore").status_code == 403
    finally:
        app.dependency_overrides.clear()
