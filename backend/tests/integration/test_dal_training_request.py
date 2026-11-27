"""Les demandes de formation sur un vrai PostgreSQL (US-014) : enregistrer,
ajuster, décider, et l'historique avec les noms."""

import uuid
from datetime import UTC, date, datetime

import pytest

from app.bll.bll_history import BllHistory
from app.bll.bll_training import BllTraining
from app.bll.bll_training_request import BllTrainingRequest
from app.bll.bll_user import AccountInput, BllUser
from app.dal.dal_audit import DalAudit
from app.dal.dal_training import DalTraining
from app.dal.dal_training_request import DalTrainingRequest
from app.dal.dal_user import DalUser
from app.entities.ent_training_request import RequestStatus
from app.entities.ent_user import EntActor, Role
from tests.unit.fakes import FakeEmail

pytestmark = pytest.mark.integration

RAMP = uuid.UUID("0b1e0c3a-0000-4000-8000-000000000012")


def test_a_request_is_recorded_adjusted_decided_and_told(session_factory) -> None:
    users = BllUser(dal=DalUser(session_factory), email=FakeEmail(), clock=lambda: datetime(2026, 11, 24, tzinfo=UTC))

    def account(badge, first, role):
        user = users.create_user(None, AccountInput(badge, first, "Test", f"{uuid.uuid4()}@example.test", None, [role]))
        return EntActor(user_id=user.id, roles=frozenset({Role(role)}))

    secretary, coordinator = account("Q41-41", "Sonia", "secretary"), account("Q42-42", "Rose", "coordinator")
    trainings = DalTraining(session_factory)
    training = BllTraining(trainings).create_training(secretary, f"Rampe {uuid.uuid4().hex[:6]}", None, RAMP)
    bll = BllTrainingRequest(DalTrainingRequest(session_factory), trainings, today=lambda: date(2026, 11, 24))

    data = {"requesting_service": "Service de sûreté", "is_external": False, "received_on": date(2026, 11, 20),
            "training_id": training.id, "expected_participants": 12, "desired_period": None, "comment": None}
    request = bll.create(secretary, data)
    assert (request.status, request.training_title, request.recorded_by_name) == (RequestStatus.PENDING, training.title, "Sonia Test (Q41-41)")
    bll.adjust(secretary, request.id, {**data, "expected_participants": 40})
    decided = bll.decide(coordinator, request.id, "approved", None)
    assert (decided.status, decided.decided_by_name, decided.expected_participants) == (RequestStatus.APPROVED, "Rose Test (Q42-42)", 40)
    assert decided.id in {r.id for r in bll.list(secretary, "approved")}
    assert decided.id not in {r.id for r in bll.list(secretary, "pending")}

    entries = BllHistory(DalAudit(session_factory)).history(secretary, "training_requests", str(request.id))
    assert [e.action.value for e in entries] == ["create", "update", "update"]
    assert [e.actor_name for e in entries] == ["Sonia Test (Q41-41)", "Sonia Test (Q41-41)", "Rose Test (Q42-42)"]
    assert entries[0].after["received_on"] == "2026-11-20"
    assert entries[2].after["status"] == "approved"
