import json
import re
from datetime import UTC, datetime

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.bll.bll_history import BllHistory
from app.bll.bll_user import AccountInput, BllUser
from app.core.exceptions import EmailDeliveryError
from app.dal.dal_audit import DalAudit, MissingAuditActorError
from app.dal.dal_user import DalUser
from app.entities.ent_audit import (
    COMMAND_LINE_LABEL,
    PASSWORD_LINK_LABEL,
    SECRET_CHANGED,
    SIGNED_IN_LABEL,
)
from app.entities.ent_user import EntActor, Role
from tests.unit.fakes import FakeEmail

pytestmark = pytest.mark.integration

NOW = datetime(2026, 11, 16, 12, 0, tzinfo=UTC)


def _account(badge="B07-42", email="marie@example.test", roles=("secretary",)) -> AccountInput:
    return AccountInput(badge, "Marie", "Joseph", email, None, roles)


@pytest.fixture
def setup(session_factory):
    email = FakeEmail()
    bll = BllUser(dal=DalUser(session_factory), email=email, clock=lambda: NOW)
    return bll, DalAudit(session_factory), email, session_factory


@pytest.fixture(autouse=True)
def _baseline(session_factory):
    """Le journal ne se vide jamais, même entre deux tests : chaque test ne
    regarde que les entrées écrites après son début."""
    global _BASELINE
    with session_factory() as session:
        _BASELINE = session.scalar(text("SELECT coalesce(max(id), 0) FROM audit_log"))


_BASELINE = 0


def _rows(session_factory) -> list[dict]:
    with session_factory() as session:
        result = session.execute(text("SELECT * FROM audit_log WHERE id > :b ORDER BY id"), {"b": _BASELINE})
        return [dict(row._mapping) for row in result]


def test_a_command_line_creation_is_logged_with_its_roles(setup) -> None:
    bll, dal_audit, _, _ = setup
    user = bll.create_user(None, _account(roles=("secretary", "trainer")))

    history = dal_audit.history("users", str(user.id))
    assert [(e.table_name, e.action.value) for e in history] == [
        ("users", "create"),
        ("user_roles", "create"),
        ("user_roles", "create"),
    ]
    assert {e.actor_label for e in history} == {COMMAND_LINE_LABEL}
    assert history[0].before is None
    assert history[0].after["badge"] == "B07-42"
    assert history[0].after["password_hash"] is None
    assert sorted(e.after["role"] for e in history[1:]) == ["secretary", "trainer"]


def test_the_password_change_is_logged_without_any_secret(setup) -> None:
    bll, dal_audit, email, session_factory = setup
    user = bll.create_user(None, _account())
    token = re.search(r"jeton=([\w-]+)", email.sent[0]["body"]).group(1)
    bll.set_password_with_link(token, "formation2026")

    change = dal_audit.history("users", str(user.id))[-1]
    assert change.action.value == "update"
    assert change.actor_label == PASSWORD_LINK_LABEL
    assert change.before["password_hash"] is None
    assert change.after["password_hash"] == SECRET_CHANGED

    everything = json.dumps(_rows(session_factory), default=str)
    assert "$argon2" not in everything
    assert token not in everything
    assert "password_tokens" not in everything


def test_role_and_activation_changes_name_the_signed_in_admin(setup) -> None:
    bll, dal_audit, _, _ = setup
    admin = bll.create_user(None, _account(badge="A01-01", email="admin@example.test", roles=("it_admin",)))
    acting = EntActor(user_id=admin.id, roles=admin.roles)
    user = bll.create_user(acting, _account())

    bll.set_roles(acting, user.id, ["trainer"])
    bll.set_active(acting, user.id, False)

    entries = dal_audit.history("users", str(user.id))[2:]
    assert [(e.table_name, e.action.value) for e in entries] == [
        ("user_roles", "delete"),
        ("user_roles", "create"),
        ("users", "update"),
    ]
    assert all(e.actor_user_id == admin.id and e.actor_label == SIGNED_IN_LABEL for e in entries)
    assert entries[0].before["role"] == "secretary" and entries[0].after is None
    assert entries[1].after["role"] == "trainer"
    assert (entries[2].before["is_active"], entries[2].after["is_active"]) == (True, False)


def test_a_failed_email_leaves_no_trace_either(session_factory) -> None:
    bll = BllUser(dal=DalUser(session_factory), email=FakeEmail(fails=True), clock=lambda: NOW)
    with pytest.raises(EmailDeliveryError):
        bll.create_user(None, _account())
    assert _rows(session_factory) == []


def test_a_change_without_a_declared_author_is_refused(setup) -> None:
    bll, _, _, session_factory = setup
    user = bll.create_user(None, _account())
    with pytest.raises(MissingAuditActorError):
        DalUser(session_factory).set_active(user.id, False, NOW)
    assert DalUser(session_factory).get_user(user.id).is_active is True


@pytest.mark.parametrize(
    "statement",
    ["UPDATE audit_log SET actor_label = 'falsifié'", "DELETE FROM audit_log", "TRUNCATE audit_log"],
)
def test_the_database_refuses_to_change_the_journal(setup, statement: str) -> None:
    bll, _, _, session_factory = setup
    bll.create_user(None, _account())
    with session_factory() as session:
        with pytest.raises(DBAPIError, match="ne se modifie ni ne se supprime"):
            session.execute(text(statement))
        session.rollback()
    assert len(_rows(session_factory)) == 2


def test_the_history_reads_in_chronological_order_for_the_admin(setup) -> None:
    bll, dal_audit, _, _ = setup
    user = bll.create_user(None, _account())
    admin_actor = EntActor(user_id=user.id, roles=frozenset({Role.IT_ADMIN}))
    bll.set_roles(EntActor(user_id=user.id, roles=frozenset({Role.IT_ADMIN})), user.id, ["direction"])

    history = BllHistory(dal_audit).history(admin_actor, "users", str(user.id))
    assert [e.action.value for e in history] == ["create", "create", "delete", "create"]


def test_a_role_created_with_its_account_records_its_user_id(setup) -> None:
    # La clé étrangère donnée par l'objet (`user=…`) doit figurer dans l'entrée
    # (constaté vide sur US-012, depuis US-003).
    bll, _, _, session_factory = setup
    user = bll.create_user(None, _account(badge="B08-42", email="fk@example.test", roles=("trainer",)))
    roles = [r for r in _rows(session_factory) if r["table_name"] == "user_roles"]
    assert [r["after"]["user_id"] for r in roles] == [str(user.id)]
