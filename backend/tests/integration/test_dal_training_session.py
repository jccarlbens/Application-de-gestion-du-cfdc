"""Les sessions sur un vrai PostgreSQL (US-015) : depuis une demande validée,
report, annulation, et l'historique avec les noms."""

import uuid
from datetime import UTC, date, datetime

import pytest

from app.bll.bll_history import BllHistory
from app.bll.bll_training import BllTraining
from app.bll.bll_training_request import BllTrainingRequest
from app.bll.bll_training_session import BllTrainingSession
from app.bll.bll_user import AccountInput, BllUser
from app.dal.dal_audit import DalAudit
from app.dal.dal_training import DalTraining
from app.dal.dal_training_request import DalTrainingRequest
from app.dal.dal_training_session import DalTrainingSession
from app.dal.dal_user import DalUser
from app.entities.ent_user import EntActor, Role
from tests.unit.fakes import FakeEmail

pytestmark = pytest.mark.integration

RAMP = uuid.UUID("0b1e0c3a-0000-4000-8000-000000000012")
TODAY = date(2026, 11, 24)


def test_a_session_from_an_approved_request_is_moved_cancelled_and_told(session_factory) -> None:
    users = BllUser(dal=DalUser(session_factory), email=FakeEmail(), clock=lambda: datetime(2026, 11, 24, tzinfo=UTC))

    def account(badge, role):
        user = users.create_user(None, AccountInput(badge, "Rose", "Test", f"{uuid.uuid4()}@example.test", None, [role]))
        return EntActor(user_id=user.id, roles=frozenset({Role(role)}))

    coordinator = account("Q51-51", "coordinator")
    trainings = DalTraining(session_factory)
    requests_dal = DalTrainingRequest(session_factory)
    training = BllTraining(trainings).create_training(coordinator, f"Rampe {uuid.uuid4().hex[:6]}", None, RAMP)
    requests = BllTrainingRequest(requests_dal, trainings, today=lambda: TODAY)
    request = requests.create(coordinator, {"requesting_service": "Sûreté", "is_external": False, "received_on": TODAY,
                                            "training_id": training.id, "expected_participants": 40, "desired_period": None, "comment": None})
    requests.decide(coordinator, request.id, "approved", None)

    bll = BllTrainingSession(DalTrainingSession(session_factory), trainings, requests_dal, today=lambda: TODAY)
    group_a = bll.plan(coordinator, None, request.id, "Groupe A", date(2026, 12, 2), date(2026, 12, 5))
    group_b = bll.plan(coordinator, None, request.id, "Groupe B", date(2026, 12, 9), date(2026, 12, 12))
    assert (group_a.training_id, group_a.request_service, group_a.planned_by_name) == (training.id, "Sûreté", "Rose Test (Q51-51)")
    assert [s.label for s in bll.list(coordinator, request_id=request.id)] == ["Groupe A", "Groupe B"]
    assert {s.id for s in bll.list(coordinator, training_id=training.id)} == {group_a.id, group_b.id}

    bll.reschedule(coordinator, group_a.id, date(2026, 12, 3), date(2026, 12, 6))
    bll.cancel(coordinator, group_b.id, "Formateur absent")

    entries = BllHistory(DalAudit(session_factory)).history(coordinator, "training_sessions", str(group_a.id))
    assert [e.action.value for e in entries] == ["create", "update"]
    assert entries[1].before["starts_on"] == "2026-12-02" and entries[1].after["starts_on"] == "2026-12-03"
    cancelled = BllHistory(DalAudit(session_factory)).history(coordinator, "training_sessions", str(group_b.id))[-1]
    assert (cancelled.after["status"], cancelled.after["cancel_reason"]) == ("cancelled", "Formateur absent")
