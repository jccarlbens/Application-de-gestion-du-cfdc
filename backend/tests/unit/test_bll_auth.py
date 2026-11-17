from datetime import UTC, datetime, timedelta

import pytest

from app.bll import bll_auth
from app.bll.bll_auth import BLOCKED, DEACTIVATED, EXPIRED, WRONG_CREDENTIALS, BllAuth
from app.bll.bll_password import hash_password
from app.bll.bll_user import BllUser
from app.core.exceptions import (
    AccountUnavailableError,
    ForbiddenError,
    InvalidCredentialsError,
    NotAuthenticatedError,
    SessionExpiredError,
)
from app.entities.ent_auth import LoginOutcome
from app.entities.ent_user import Role
from tests.unit.fakes import FakeDalAuth, FakeDalUser, FakeEmail, actor

START = datetime(2026, 11, 17, 9, 0, tzinfo=UTC)
PASSWORD = "formation2026"
HASH = hash_password(PASSWORD)


@pytest.fixture
def world():
    users, auth = FakeDalUser(), FakeDalAuth()
    users.auth = auth
    clock = {"now": START}
    bll = BllAuth(dal_user=users, dal_auth=auth, clock=lambda: clock["now"])
    user = users.add_user_with_password("B07-42", HASH, roles=(Role.SECRETARY, Role.TRAINER))
    return bll, users, auth, clock, user


def _fail(bll, times: int, badge="B07-42") -> None:
    for _ in range(times):
        with pytest.raises(InvalidCredentialsError):
            bll.login(badge, "mauvais-mot-2")


def test_good_credentials_open_a_session_for_that_account(world) -> None:
    bll, _, auth, _, user = world
    result = bll.login("b07-42 ", PASSWORD)

    assert result.user.id == user.id
    assert bll.authenticate(result.token).roles == {Role.SECRETARY, Role.TRAINER}
    assert auth.attempts[-1]["outcome"] is LoginOutcome.SUCCESS
    assert result.token not in str(auth.sessions)  # seule l'empreinte est gardée


@pytest.mark.parametrize("badge,password", [("B07-42", "mauvais-mot-2"), ("Z99-99", PASSWORD)])
def test_wrong_badge_or_password_give_the_same_message(world, badge, password) -> None:
    bll, *_ = world
    with pytest.raises(InvalidCredentialsError) as error:
        bll.login(badge, password)
    assert str(error.value) == WRONG_CREDENTIALS == "Numéro de badge ou mot de passe incorrect."


def test_an_unknown_badge_costs_a_password_check_too(world, monkeypatch) -> None:
    bll, *_ = world
    calls = []
    monkeypatch.setattr(bll_auth, "burn_verification_time", lambda password: calls.append(password))
    with pytest.raises(InvalidCredentialsError):
        bll.login("Z99-99", "quelconque1")
    assert calls == ["quelconque1"]


def test_an_account_without_password_yet_cannot_log_in(world) -> None:
    bll, users, *_ = world
    user = users.add_user_with_password("C01-01", HASH)
    users.password_hashes[user.id] = None
    with pytest.raises(InvalidCredentialsError, match="Numéro de badge"):
        bll.login("C01-01", PASSWORD)


def test_the_fifth_consecutive_failure_blocks_the_account(world) -> None:
    bll, users, _, _, user = world
    _fail(bll, 4)
    assert not users.users[user.id].is_blocked
    _fail(bll, 1)
    assert users.users[user.id].is_blocked
    with pytest.raises(AccountUnavailableError) as error:
        bll.login("B07-42", PASSWORD)
    assert str(error.value) == BLOCKED


def test_a_blocked_account_with_a_wrong_password_still_gets_the_generic_message(world) -> None:
    bll, *_ = world
    _fail(bll, 5)
    with pytest.raises(InvalidCredentialsError):
        bll.login("B07-42", "encore-faux-3")


def test_a_success_resets_the_count(world) -> None:
    bll, users, _, _, user = world
    _fail(bll, 4)
    bll.login("B07-42", PASSWORD)
    _fail(bll, 4)
    assert not users.users[user.id].is_blocked


def test_blocking_closes_open_sessions(world) -> None:
    bll, *_ = world
    token = bll.login("B07-42", PASSWORD).token
    _fail(bll, 5)
    with pytest.raises(SessionExpiredError):
        bll.authenticate(token)


def test_only_the_admin_unblocks_and_the_count_restarts(world) -> None:
    bll, users, auth, clock, user = world
    _fail(bll, 5)
    accounts = BllUser(dal=users, email=FakeEmail(), clock=lambda: clock["now"])
    with pytest.raises(ForbiddenError):
        accounts.unblock(actor(Role.COORDINATOR), user.id)

    clock["now"] = START + timedelta(minutes=1)
    accounts.unblock(actor(Role.IT_ADMIN), user.id)
    clock["now"] = START + timedelta(minutes=2)
    _fail(bll, 4)
    assert not users.users[user.id].is_blocked
    assert bll.login("B07-42", PASSWORD).user.id == user.id


def test_a_deactivated_account_is_told_so_once_the_password_is_right(world) -> None:
    bll, users, _, clock, user = world
    token = bll.login("B07-42", PASSWORD).token
    BllUser(dal=users, email=FakeEmail(), clock=lambda: clock["now"]).set_active(actor(Role.IT_ADMIN), user.id, False)

    with pytest.raises(SessionExpiredError):
        bll.authenticate(token)
    with pytest.raises(AccountUnavailableError) as error:
        bll.login("B07-42", PASSWORD)
    assert str(error.value) == DEACTIVATED


def test_the_session_slides_and_expires_after_15_idle_minutes(world) -> None:
    bll, _, _, clock, _ = world
    token = bll.login("B07-42", PASSWORD).token

    clock["now"] = START + timedelta(minutes=14)
    bll.authenticate(token)
    clock["now"] = START + timedelta(minutes=28)  # 14 minutes après la dernière activité
    bll.authenticate(token)
    clock["now"] = START + timedelta(minutes=43, seconds=1)  # 15 minutes et 1 seconde sans activité
    with pytest.raises(SessionExpiredError) as error:
        bll.authenticate(token)
    assert str(error.value) == EXPIRED == "Votre session a expiré, reconnectez-vous."


def test_no_cookie_means_not_connected(world) -> None:
    bll, *_ = world
    with pytest.raises(NotAuthenticatedError, match="pas connecté"):
        bll.authenticate(None)


def test_logout_closes_the_session(world) -> None:
    bll, *_ = world
    token = bll.login("B07-42", PASSWORD).token
    bll.logout(token)
    with pytest.raises(SessionExpiredError):
        bll.authenticate(token)


def test_attempts_never_keep_the_password(world) -> None:
    bll, _, auth, _, _ = world
    _fail(bll, 2)
    bll.login("B07-42", PASSWORD)
    assert PASSWORD not in str(auth.attempts) and "mauvais-mot-2" not in str(auth.attempts)
