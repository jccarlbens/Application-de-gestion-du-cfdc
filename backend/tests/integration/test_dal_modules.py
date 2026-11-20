"""Les modules sur un vrai PostgreSQL (US-011) : unicité du titre dans la
formation, ordre d'ajout, journal sous la formation, formateur désactivé."""

import uuid
from datetime import UTC, datetime

import pytest

from app.bll.bll_history import BllHistory
from app.bll.bll_training import BllTraining
from app.bll.bll_user import AccountInput, BllUser
from app.core.exceptions import DuplicateNameError
from app.dal.dal_audit import DalAudit
from app.dal.dal_training import DalTraining
from app.dal.dal_user import DalUser
from app.entities.ent_user import EntActor, Role
from tests.unit.fakes import FakeEmail

pytestmark = pytest.mark.integration

RAMP = uuid.UUID("0b1e0c3a-0000-4000-8000-000000000012")


def _account(users: BllUser, badge: str, first: str, last: str, role: str):
    return users.create_user(None, AccountInput(badge, first, last, f"{uuid.uuid4()}@example.test", None, [role]))


@pytest.fixture
def setup(session_factory):
    users = BllUser(dal=DalUser(session_factory), email=FakeEmail(), clock=lambda: datetime(2026, 11, 20, tzinfo=UTC))
    secretary = _account(users, "Q11-11", "Sonia", "Saintil", "secretary")
    admin = _account(users, "Q12-12", "Ada", "Admin", "it_admin")
    paul = _account(users, "Q13-13", "Paul", "Michel", "trainer")
    rose = _account(users, "Q14-14", "Rose", "Pierre", "trainer")
    bll = BllTraining(DalTraining(session_factory))
    as_secretary = EntActor(user_id=secretary.id, roles=frozenset({Role.SECRETARY}))
    as_admin = EntActor(user_id=admin.id, roles=frozenset({Role.IT_ADMIN}))
    training = bll.create_training(as_secretary, f"Rampe {uuid.uuid4().hex[:6]}", None, RAMP)
    return {
        "bll": bll, "history": BllHistory(DalAudit(session_factory)), "users": users,
        "secretary": as_secretary, "admin": as_admin, "paul": paul, "rose": rose, "training": training,
        "admin_entity": admin,
    }


def test_modules_keep_the_order_they_were_added(setup) -> None:
    bll, training, secretary = setup["bll"], setup["training"], setup["secretary"]
    for title in ["Vitesses", "Annonces", "Balisage"]:
        bll.add_module(secretary, training.id, title, None, None)
    assert [m.title for m in bll.list_modules(secretary, training.id)] == ["Vitesses", "Annonces", "Balisage"]


def test_the_database_refuses_a_duplicate_title_in_the_same_training(setup) -> None:
    bll, training, secretary = setup["bll"], setup["training"], setup["secretary"]
    bll.add_module(secretary, training.id, "Vitesses", None, None)
    with pytest.raises(DuplicateNameError, match="déjà un module"):
        bll.add_module(secretary, training.id, "VITESSES", None, None)


def test_module_changes_are_told_in_the_history_of_the_training(setup) -> None:
    s = setup
    module = s["bll"].add_module(s["secretary"], s["training"].id, "Vitesses", None, None)
    s["bll"].assign_trainer(s["secretary"], module.id, s["paul"].id)
    s["bll"].assign_trainer(s["admin"], module.id, s["rose"].id)
    entries = s["history"].history(s["secretary"], "trainings", str(s["training"].id))
    modules = [e for e in entries if e.table_name == "modules"]
    assert [e.action.value for e in modules] == ["create", "update", "update"]
    assert [e.actor_name for e in modules] == ["Sonia Saintil (Q11-11)", "Sonia Saintil (Q11-11)", "Ada Admin (Q12-12)"]
    assert modules[1].after["trainer_id"] == str(s["paul"].id)
    assert modules[2].before["trainer_id"] == str(s["paul"].id)


def test_a_deactivated_trainer_stays_on_the_module_and_is_flagged(setup) -> None:
    s = setup
    module = s["bll"].add_module(s["secretary"], s["training"].id, "Vitesses", None, s["paul"].id)
    s["users"].set_active(EntActor(user_id=s["admin_entity"].id, roles=frozenset({Role.IT_ADMIN})), s["paul"].id, False)
    [listed] = [m for m in s["bll"].list_modules(s["secretary"], s["training"].id) if m.id == module.id]
    assert (listed.trainer.badge, listed.trainer.is_active, listed.trainer.is_trainer) == ("Q13-13", False, True)
    assert s["paul"].id not in {t.id for t in s["bll"].list_trainers(s["secretary"])}


def test_a_trainer_who_loses_the_role_is_flagged(setup) -> None:
    s = setup
    s["bll"].add_module(s["secretary"], s["training"].id, "Vitesses", None, s["paul"].id)
    s["users"].set_roles(EntActor(user_id=s["admin_entity"].id, roles=frozenset({Role.IT_ADMIN})), s["paul"].id, ["secretary"])
    [listed] = s["bll"].list_modules(s["secretary"], s["training"].id)
    assert (listed.trainer.is_active, listed.trainer.is_trainer) == (True, False)
