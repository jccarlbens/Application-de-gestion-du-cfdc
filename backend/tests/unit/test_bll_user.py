import re
from datetime import UTC, datetime, timedelta

import pytest

from app.bll.bll_password import verify_password
from app.bll.bll_user import AccountInput, BllUser
from app.core.exceptions import (
    AdminAlreadyExistsError,
    DuplicateBadgeError,
    DuplicateEmailError,
    EmailDeliveryError,
    ForbiddenError,
    InvalidInputError,
    InvalidPasswordLinkError,
    LastAdminError,
    WeakPasswordError,
)
from app.entities.ent_user import Role
from tests.unit.fakes import FakeDalUser, FakeEmail, actor

NOW = datetime(2026, 11, 13, 12, 0, tzinfo=UTC)
ADMIN = actor(Role.IT_ADMIN)
COORDINATOR = actor(Role.COORDINATOR)


def _account(badge="B07-42", email="marie@example.test", roles=("secretary",)) -> AccountInput:
    return AccountInput(badge, "Marie", "Joseph", email, None, roles)


@pytest.fixture
def setup():
    dal, email = FakeDalUser(), FakeEmail()
    clock = {"now": NOW}
    bll = BllUser(dal=dal, email=email, clock=lambda: clock["now"])
    return bll, dal, email, clock


def _token_from(email: FakeEmail) -> str:
    return re.search(r"jeton=([\w-]+)", email.sent[-1]["body"]).group(1)


# --- Création -----------------------------------------------------------------


def test_admin_creates_an_account_and_a_link_is_emailed(setup) -> None:
    bll, dal, email, _ = setup
    user = bll.create_user(ADMIN, _account(roles=("secretary", "trainer")))

    assert user.roles == {Role.SECRETARY, Role.TRAINER}
    assert user.has_password is False
    assert email.sent[0]["to"] == "marie@example.test"
    assert "/mot-de-passe?jeton=" in email.sent[0]["body"]
    assert "B07-42" in email.sent[0]["body"]


@pytest.mark.parametrize("badge", ["A00-00", "B07-42", "z12-34"])
def test_badge_accepts_any_letter_and_is_stored_in_capitals(setup, badge: str) -> None:
    bll, *_ = setup
    assert bll.create_user(ADMIN, _account(badge=badge)).badge == badge.upper()


@pytest.mark.parametrize("badge", ["A0-00", "AA0-00", "A00_00", "100-00", "A00-000", ""])
def test_badge_with_the_wrong_format_is_refused(setup, badge: str) -> None:
    bll, *_ = setup
    with pytest.raises(InvalidInputError, match="A00-00"):
        bll.create_user(ADMIN, _account(badge=badge))


def test_badge_and_email_must_be_unique(setup) -> None:
    bll, *_ = setup
    bll.create_user(ADMIN, _account())
    with pytest.raises(DuplicateBadgeError):
        bll.create_user(ADMIN, _account(email="autre@example.test"))
    with pytest.raises(DuplicateEmailError):
        bll.create_user(ADMIN, _account(badge="C01-01", email="MARIE@example.test "))


@pytest.mark.parametrize(
    "account",
    [
        AccountInput("B07-42", " ", "Joseph", "m@example.test", None, ["secretary"]),
        AccountInput("B07-42", "Marie", "Joseph", "pas-un-email", None, ["secretary"]),
        AccountInput("B07-42", "Marie", "Joseph", "m@example.test", None, []),
        AccountInput("B07-42", "Marie", "Joseph", "m@example.test", None, ["pilote"]),
    ],
)
def test_invalid_accounts_are_refused(setup, account: AccountInput) -> None:
    bll, *_ = setup
    with pytest.raises(InvalidInputError):
        bll.create_user(ADMIN, account)


def test_coordinator_creates_accounts_but_never_an_admin(setup) -> None:
    bll, *_ = setup
    assert bll.create_user(COORDINATOR, _account(roles=("trainer",))).roles == {Role.TRAINER}
    with pytest.raises(ForbiddenError):
        bll.create_user(COORDINATOR, _account(badge="C01-01", email="c@example.test", roles=("it_admin",)))


@pytest.mark.parametrize("role", [Role.SECRETARY, Role.SERVICE_HEAD, Role.TRAINER, Role.DIRECTION])
def test_other_roles_cannot_create_accounts(setup, role: Role) -> None:
    bll, *_ = setup
    with pytest.raises(ForbiddenError):
        bll.create_user(actor(role), _account())


def test_nothing_is_saved_when_the_email_cannot_be_sent() -> None:
    dal = FakeDalUser()
    bll = BllUser(dal=dal, email=FakeEmail(fails=True), clock=lambda: NOW)
    with pytest.raises(EmailDeliveryError):
        bll.create_user(ADMIN, _account())
    assert dal.users == {}


def test_create_first_admin_only_once(setup) -> None:
    bll, *_ = setup
    admin = bll.create_first_admin(_account(roles=()))
    assert Role.IT_ADMIN in admin.roles
    with pytest.raises(AdminAlreadyExistsError):
        bll.create_first_admin(_account(badge="C01-01", email="c@example.test"))


def test_command_line_creates_any_account(setup) -> None:
    bll, *_ = setup
    assert bll.create_user(None, _account(roles=("it_admin", "direction"))).roles == {Role.IT_ADMIN, Role.DIRECTION}


# --- Gestion par l'administrateur ---------------------------------------------------


def test_only_admin_and_coordinator_list_accounts(setup) -> None:
    bll, *_ = setup
    bll.create_user(ADMIN, _account())
    assert len(bll.list_users(ADMIN)) == 1
    assert len(bll.list_users(COORDINATOR)) == 1
    with pytest.raises(ForbiddenError):
        bll.list_users(actor(Role.SECRETARY))


def test_only_admin_changes_roles_and_activation(setup) -> None:
    bll, *_ = setup
    user = bll.create_user(ADMIN, _account())
    assert bll.set_roles(ADMIN, user.id, ["trainer", "direction"]).roles == {Role.TRAINER, Role.DIRECTION}
    assert bll.set_active(ADMIN, user.id, False).is_active is False
    assert bll.set_active(ADMIN, user.id, True).is_active is True
    for not_admin in (COORDINATOR, actor(Role.SECRETARY)):
        with pytest.raises(ForbiddenError):
            bll.set_roles(not_admin, user.id, ["trainer"])
        with pytest.raises(ForbiddenError):
            bll.set_active(not_admin, user.id, False)


def test_the_last_active_admin_cannot_be_deactivated_nor_lose_the_role(setup) -> None:
    bll, *_ = setup
    admin = bll.create_first_admin(_account(badge="A01-01", email="admin@example.test"))
    with pytest.raises(LastAdminError):
        bll.set_active(ADMIN, admin.id, False)
    with pytest.raises(LastAdminError):
        bll.set_roles(ADMIN, admin.id, ["coordinator"])


def test_an_admin_can_go_once_another_admin_is_active(setup) -> None:
    bll, *_ = setup
    first = bll.create_first_admin(_account(badge="A01-01", email="admin@example.test"))
    bll.create_user(ADMIN, _account(badge="A01-02", email="admin2@example.test", roles=("it_admin",)))
    assert bll.set_active(ADMIN, first.id, False).is_active is False


# --- Mot de passe par le lien -------------------------------------------------------


def test_the_link_sets_an_argon2id_password_once(setup) -> None:
    bll, dal, email, _ = setup
    user = bll.create_user(ADMIN, _account())
    token = _token_from(email)

    bll.set_password_with_link(token, "formation2026")

    stored = dal.password_hashes[user.id]
    assert stored.startswith("$argon2id$")
    assert verify_password(stored, "formation2026")
    with pytest.raises(InvalidPasswordLinkError):
        bll.set_password_with_link(token, "autrechose1")


def test_the_link_expires_after_48_hours(setup) -> None:
    bll, _, email, clock = setup
    bll.create_user(ADMIN, _account())
    clock["now"] = NOW + timedelta(hours=48, seconds=1)
    with pytest.raises(InvalidPasswordLinkError):
        bll.set_password_with_link(_token_from(email), "formation2026")


def test_an_unknown_link_is_refused(setup) -> None:
    bll, *_ = setup
    with pytest.raises(InvalidPasswordLinkError):
        bll.set_password_with_link("inconnu", "formation2026")


@pytest.mark.parametrize("password", ["court1", "sanschiffre", ""])
def test_a_weak_password_is_refused_and_the_link_stays_usable(setup, password: str) -> None:
    bll, _, email, _ = setup
    bll.create_user(ADMIN, _account())
    token = _token_from(email)
    with pytest.raises(WeakPasswordError):
        bll.set_password_with_link(token, password)
    bll.set_password_with_link(token, "formation2026")
