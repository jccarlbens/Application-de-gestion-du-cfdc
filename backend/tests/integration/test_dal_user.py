import re
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text

from app.bll.bll_password import verify_password
from app.bll.bll_user import AccountInput, BllUser
from app.core.exceptions import (
    DuplicateBadgeError,
    DuplicateEmailError,
    EmailDeliveryError,
    InvalidPasswordLinkError,
    LastAdminError,
)
from app.dal.dal_user import DalUser, UserModel
from app.entities.ent_user import EntActor, Role
from tests.unit.fakes import FakeEmail

pytestmark = pytest.mark.integration

NOW = datetime(2026, 11, 13, 12, 0, tzinfo=UTC)


def _account(badge="B07-42", email="marie@example.test", roles=("secretary", "trainer")) -> AccountInput:
    return AccountInput(badge, "Marie", "Joseph", email, "+509 3700 0000", roles)


@pytest.fixture
def setup(session_factory):
    dal, email = DalUser(session_factory), FakeEmail()
    clock = {"now": NOW}
    return BllUser(dal=dal, email=email, clock=lambda: clock["now"]), dal, email, clock, session_factory


def test_an_account_and_its_roles_are_stored(setup) -> None:
    bll, dal, *_ = setup
    created = bll.create_user(None, _account())

    stored = dal.get_user(created.id)
    assert stored.badge == "B07-42"
    assert stored.roles == {Role.SECRETARY, Role.TRAINER}
    assert stored.is_active and not stored.is_blocked and not stored.has_password
    assert stored.created_at.tzinfo is not None
    assert [u.badge for u in dal.list_users()] == ["B07-42"]


def test_the_database_refuses_duplicate_badges_and_emails(setup) -> None:
    bll, *_ = setup
    bll.create_user(None, _account())
    with pytest.raises(DuplicateBadgeError):
        bll.create_user(None, _account(email="autre@example.test"))
    with pytest.raises(DuplicateEmailError):
        bll.create_user(None, _account(badge="C01-01"))


def test_a_failed_email_leaves_no_account(session_factory) -> None:
    dal = DalUser(session_factory)
    bll = BllUser(dal=dal, email=FakeEmail(fails=True), clock=lambda: NOW)
    with pytest.raises(EmailDeliveryError):
        bll.create_user(None, _account())
    assert dal.list_users() == []


def test_roles_and_activation_change_and_the_last_admin_is_protected(setup) -> None:
    bll, dal, *_ = setup
    admin = bll.create_first_admin(_account(badge="A01-01", email="admin@example.test", roles=()))
    acting = EntActor(user_id=admin.id, roles=admin.roles)

    with pytest.raises(LastAdminError):
        bll.set_active(acting, admin.id, False)
    assert dal.count_active_admins() == 1

    other = bll.create_user(acting, _account())
    assert bll.set_roles(acting, other.id, ["it_admin"]).roles == {Role.IT_ADMIN}
    assert dal.count_active_admins() == 2
    assert bll.set_active(acting, admin.id, False).is_active is False
    assert dal.count_active_admins() == 1


def test_the_link_stores_an_argon2id_hash_only_once_and_expires(setup) -> None:
    bll, dal, email, clock, session_factory = setup
    user = bll.create_user(None, _account())
    token = re.search(r"jeton=([\w-]+)", email.sent[0]["body"]).group(1)

    bll.set_password_with_link(token, "formation2026")
    with session_factory() as session:
        stored_hash = session.get(UserModel, user.id).password_hash
    assert stored_hash.startswith("$argon2id$") and verify_password(stored_hash, "formation2026")
    assert dal.get_user(user.id).has_password
    with pytest.raises(InvalidPasswordLinkError):
        bll.set_password_with_link(token, "formation2027")

    second = bll.create_user(None, _account(badge="C01-01", email="c@example.test"))
    late_token = re.search(r"jeton=([\w-]+)", email.sent[1]["body"]).group(1)
    clock["now"] = NOW + timedelta(hours=49)
    with pytest.raises(InvalidPasswordLinkError):
        bll.set_password_with_link(late_token, "formation2026")
    assert not dal.get_user(second.id).has_password


def test_only_a_hash_of_the_link_is_stored(setup) -> None:
    bll, _, email, _, session_factory = setup
    bll.create_user(None, _account())
    token = re.search(r"jeton=([\w-]+)", email.sent[0]["body"]).group(1)
    with session_factory() as session:
        stored = session.execute(text("SELECT token_hash FROM password_tokens")).scalar_one()
    assert stored != token and len(stored) == 64
