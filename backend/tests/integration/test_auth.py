import re
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text

from app.bll.bll_auth import BllAuth
from app.bll.bll_user import AccountInput, BllUser
from app.core.exceptions import AccountUnavailableError, InvalidCredentialsError, SessionExpiredError
from app.dal.dal_audit import DalAudit
from app.dal.dal_auth import DalAuth
from app.dal.dal_user import DalUser
from app.entities.ent_audit import AUTO_BLOCK_LABEL
from app.entities.ent_user import EntActor, Role
from tests.unit.fakes import FakeEmail

pytestmark = pytest.mark.integration

START = datetime(2026, 11, 17, 9, 0, tzinfo=UTC)
PASSWORD = "formation2026"


@pytest.fixture
def world(session_factory):
    clock = {"now": START}
    now = lambda: clock["now"]  # noqa: E731
    users, email = DalUser(session_factory), FakeEmail()
    accounts = BllUser(dal=users, email=email, clock=now)
    auth = BllAuth(dal_user=users, dal_auth=DalAuth(session_factory), clock=now)
    user = accounts.create_user(None, AccountInput("B07-42", "Marie", "Joseph", "marie@example.test", None, ["secretary"]))
    token = re.search(r"jeton=([\w-]+)", email.sent[0]["body"]).group(1)
    accounts.set_password_with_link(token, PASSWORD)
    return auth, accounts, user, clock, session_factory


def _fail(auth, times: int) -> None:
    for _ in range(times):
        with pytest.raises(InvalidCredentialsError):
            auth.login("B07-42", "mauvais-mot-2")


def test_a_real_login_opens_a_session_that_slides_then_expires(world) -> None:
    auth, _, user, clock, _ = world
    token = auth.login("b07-42", PASSWORD).token
    assert auth.authenticate(token).user_id == user.id

    clock["now"] = START + timedelta(minutes=10)
    auth.authenticate(token)
    clock["now"] = START + timedelta(minutes=25, seconds=1)
    with pytest.raises(SessionExpiredError):
        auth.authenticate(token)


def test_five_failures_block_the_account_with_a_journal_entry_and_close_sessions(world) -> None:
    auth, _, user, _, session_factory = world
    token = auth.login("B07-42", PASSWORD).token
    _fail(auth, 5)

    with pytest.raises(AccountUnavailableError, match="bloqué"):
        auth.login("B07-42", PASSWORD)
    with pytest.raises(SessionExpiredError):
        auth.authenticate(token)
    block = DalAudit(session_factory).history("users", str(user.id))[-1]
    assert block.actor_label == AUTO_BLOCK_LABEL
    assert (block.before["is_blocked"], block.after["is_blocked"]) == (False, True)


def test_unblocking_restarts_the_count(world) -> None:
    auth, accounts, user, clock, _ = world
    admin = EntActor(user_id=user.id, roles=frozenset({Role.IT_ADMIN}))
    _fail(auth, 5)
    clock["now"] = START + timedelta(minutes=1)
    accounts.unblock(admin, user.id)
    clock["now"] = START + timedelta(minutes=2)
    _fail(auth, 4)
    assert auth.login("B07-42", PASSWORD).user.id == user.id


def test_deactivation_closes_sessions_immediately(world) -> None:
    auth, accounts, user, _, _ = world
    token = auth.login("B07-42", PASSWORD).token
    other_admin = EntActor(user_id=user.id, roles=frozenset({Role.IT_ADMIN}))
    accounts.set_active(other_admin, user.id, False)
    with pytest.raises(SessionExpiredError):
        auth.authenticate(token)


def test_attempts_and_sessions_keep_no_password_and_no_raw_token(world) -> None:
    auth, _, user, _, session_factory = world
    _fail(auth, 1)
    token = auth.login("B07-42", PASSWORD).token
    with session_factory() as session:
        attempts = session.execute(
            text("SELECT badge_entered, success, outcome FROM login_attempts WHERE user_id = :u ORDER BY id"),
            {"u": user.id},
        ).all()
        stored = session.execute(text("SELECT token_hash FROM auth_sessions WHERE user_id = :u"), {"u": user.id}).all()
    assert [tuple(a) for a in attempts] == [("B07-42", False, "wrong_password"), ("B07-42", True, "success")]
    assert PASSWORD not in str(attempts)
    assert len(stored) == 1 and stored[0][0] != token and len(stored[0][0]) == 64
