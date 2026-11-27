"""Les règles des demandes de formation (US-014)."""

import uuid
from dataclasses import replace
from datetime import UTC, date, datetime

import pytest
from fastapi.testclient import TestClient

from app.api.v1.security import get_current_actor
from app.api.v1.training_requests import get_bll_training_request
from app.bll.bll_training_request import BllTrainingRequest
from app.core.exceptions import ForbiddenError, InvalidInputError, RecordNotFoundError
from app.entities.ent_training_request import EntTrainingRequest, RequestStatus
from app.entities.ent_user import Role
from app.main import app
from tests.unit.fakes import actor

TODAY = date(2026, 11, 24)
NOW = datetime(2026, 11, 24, 15, 0, tzinfo=UTC)
TRAINING = uuid.uuid4()


class FakeTrainings:
    def training_exists(self, training_id) -> bool:
        return training_id == TRAINING


class FakeDal:
    def __init__(self) -> None:
        self.rows: dict[uuid.UUID, EntTrainingRequest] = {}

    def list(self, status=None):
        rows = [r for r in self.rows.values() if status is None or r.status is status]
        return sorted(rows, key=lambda r: r.received_on, reverse=True)

    def get(self, request_id):
        if request_id not in self.rows:
            raise RecordNotFoundError("Cette demande de formation n'existe pas.")
        return self.rows[request_id]

    def create(self, data, recorded_by):
        row = EntTrainingRequest(
            id=uuid.uuid4(), training_title="Rampe", status=RequestStatus.PENDING, decided_by_name=None,
            decided_at=None, decision_reason=None, recorded_by_name="X", created_at=NOW, **data.__dict__,
        )
        self.rows[row.id] = row
        return row

    def update(self, request_id, data):
        self.rows[request_id] = replace(self.rows[request_id], **data.__dict__)
        return self.rows[request_id]

    def decide(self, request_id, status, decided_by, reason, now):
        self.rows[request_id] = replace(
            self.rows[request_id], status=status, decided_by_name=str(decided_by), decided_at=now, decision_reason=reason
        )
        return self.rows[request_id]


@pytest.fixture
def bll():
    return BllTrainingRequest(FakeDal(), FakeTrainings(), today=lambda: TODAY, clock=lambda: NOW)


def _data(**overrides):
    return {
        "requesting_service": "  Service   de sûreté ", "is_external": False, "received_on": date(2026, 11, 20),
        "training_id": TRAINING, "expected_participants": 12, "desired_period": " mars 2027 ", "comment": " ",
        **overrides,
    }


@pytest.mark.parametrize("role", [Role.SECRETARY, Role.COORDINATOR, Role.SERVICE_HEAD, Role.IT_ADMIN])
def test_these_roles_record_a_pending_request(bll, role) -> None:
    request = bll.create(actor(role), _data())
    assert request.status is RequestStatus.PENDING
    assert (request.requesting_service, request.desired_period, request.comment) == ("Service de sûreté", "mars 2027", None)


@pytest.mark.parametrize("role", [Role.DIRECTION, Role.TRAINER])
def test_direction_and_trainers_do_not_record(bll, role) -> None:
    with pytest.raises(ForbiddenError):
        bll.create(actor(role), _data())


def test_the_reception_date_defaults_to_today_and_cannot_be_in_the_future(bll) -> None:
    assert bll.create(actor(Role.SECRETARY), _data(received_on=None)).received_on == TODAY
    with pytest.raises(InvalidInputError, match="futur"):
        bll.create(actor(Role.SECRETARY), _data(received_on=date(2026, 11, 25)))


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"requesting_service": "  "}, "service demandeur est obligatoire"),
        ({"requesting_service": "s" * 151}, "150 caractères"),
        ({"expected_participants": 0}, "de 1 à 500"),
        ({"expected_participants": 501}, "de 1 à 500"),
        ({"expected_participants": None}, "de 1 à 500"),
        ({"desired_period": "p" * 101}, "100 caractères"),
        ({"comment": "c" * 2001}, "2000 caractères"),
        ({"training_id": uuid.uuid4()}, "formation du catalogue"),
        ({"training_id": None}, "formation du catalogue"),
    ],
)
def test_input_is_checked_in_french(bll, overrides, message) -> None:
    with pytest.raises(InvalidInputError, match=message):
        bll.create(actor(Role.SECRETARY), _data(**overrides))


@pytest.mark.parametrize("role", [Role.COORDINATOR, Role.IT_ADMIN])
def test_coordinator_and_admin_approve_or_refuse(bll, role) -> None:
    one = bll.create(actor(Role.SECRETARY), _data())
    two = bll.create(actor(Role.SECRETARY), _data())
    assert bll.decide(actor(role), one.id, "approved", None).status is RequestStatus.APPROVED
    refused = bll.decide(actor(role), two.id, "refused", " Pas de formateur disponible ")
    assert (refused.status, refused.decision_reason, refused.decided_at) == (RequestStatus.REFUSED, "Pas de formateur disponible", NOW)


@pytest.mark.parametrize("role", [Role.SECRETARY, Role.SERVICE_HEAD, Role.DIRECTION])
def test_others_do_not_decide(bll, role) -> None:
    request = bll.create(actor(Role.SECRETARY), _data())
    with pytest.raises(ForbiddenError, match="décident"):
        bll.decide(actor(role), request.id, "approved", None)


def test_a_refusal_needs_a_reason_and_pending_is_not_a_decision(bll) -> None:
    request = bll.create(actor(Role.SECRETARY), _data())
    with pytest.raises(InvalidInputError, match="motif"):
        bll.decide(actor(Role.COORDINATOR), request.id, "refused", "  ")
    with pytest.raises(InvalidInputError, match="en attente"):
        bll.decide(actor(Role.COORDINATOR), request.id, "pending", None)
    with pytest.raises(InvalidInputError):
        bll.decide(actor(Role.COORDINATOR), request.id, "peut-être", None)


def test_a_decision_is_final_except_for_the_admin(bll) -> None:
    request = bll.create(actor(Role.SECRETARY), _data())
    bll.decide(actor(Role.COORDINATOR), request.id, "approved", None)
    with pytest.raises(ForbiddenError, match="seul l'administrateur"):
        bll.decide(actor(Role.COORDINATOR), request.id, "refused", "Erreur")
    corrected = bll.decide(actor(Role.IT_ADMIN), request.id, "refused", "Demande en double")
    assert corrected.status is RequestStatus.REFUSED
    with pytest.raises(InvalidInputError, match="en attente"):
        bll.decide(actor(Role.IT_ADMIN), request.id, "pending", None)


@pytest.mark.parametrize("role", [Role.SECRETARY, Role.COORDINATOR, Role.IT_ADMIN])
def test_these_roles_adjust_even_after_the_decision_without_touching_the_status(bll, role) -> None:
    request = bll.create(actor(Role.SECRETARY), _data())
    bll.decide(actor(Role.COORDINATOR), request.id, "approved", None)
    adjusted = bll.adjust(actor(role), request.id, _data(expected_participants=40))
    assert (adjusted.expected_participants, adjusted.status) == (40, RequestStatus.APPROVED)


@pytest.mark.parametrize("role", [Role.SERVICE_HEAD, Role.DIRECTION, Role.TRAINER])
def test_others_do_not_adjust(bll, role) -> None:
    request = bll.create(actor(Role.SECRETARY), _data())
    with pytest.raises(ForbiddenError):
        bll.adjust(actor(role), request.id, _data())


def test_listing_filters_by_status_and_trainers_do_not_see(bll) -> None:
    pending = bll.create(actor(Role.SECRETARY), _data())
    other = bll.create(actor(Role.SECRETARY), _data(received_on=date(2026, 11, 22)))
    bll.decide(actor(Role.COORDINATOR), other.id, "approved", None)
    assert [r.id for r in bll.list(actor(Role.DIRECTION), "pending")] == [pending.id]
    assert [r.id for r in bll.list(actor(Role.DIRECTION))] == [other.id, pending.id]
    with pytest.raises(InvalidInputError):
        bll.list(actor(Role.DIRECTION), "inconnu")
    with pytest.raises(ForbiddenError):
        bll.list(actor(Role.TRAINER))


def test_routes_answer_in_french() -> None:
    bll = BllTrainingRequest(FakeDal(), FakeTrainings(), today=lambda: TODAY, clock=lambda: NOW)
    app.dependency_overrides[get_bll_training_request] = lambda: bll
    app.dependency_overrides[get_current_actor] = lambda: actor(Role.SECRETARY)
    try:
        client = TestClient(app)
        body = {"requesting_service": "Sûreté", "training_id": str(TRAINING), "expected_participants": 12, "received_on": "2026-11-20"}
        created = client.post("/api/v1/training-requests", json=body)
        assert created.status_code == 201 and created.json()["status"] == "pending"
        bad = client.post("/api/v1/training-requests", json={**body, "expected_participants": 0})
        assert bad.status_code == 422 and "de 1 à 500" in bad.json()["detail"]
        decision = client.post(f"/api/v1/training-requests/{created.json()['id']}/decision", json={"status": "approved"})
        assert decision.status_code == 403
    finally:
        app.dependency_overrides.clear()
