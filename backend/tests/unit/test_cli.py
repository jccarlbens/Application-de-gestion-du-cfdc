from app.bll.bll_user import BllUser
from app.cli import EXIT_FAILED, EXIT_OK, main
from app.entities.ent_user import Role
from tests.unit.fakes import FakeDalUser, FakeEmail

ADMIN_ARGS = ["--badge", "A01-01", "--first-name", "Jean", "--last-name", "Paul", "--email", "admin@example.test"]


def _bll() -> tuple[BllUser, FakeDalUser, FakeEmail]:
    dal, email = FakeDalUser(), FakeEmail()
    return BllUser(dal=dal, email=email), dal, email


def test_create_admin_then_refuses_a_second_time(capsys) -> None:
    bll, dal, email = _bll()
    assert main(["create-admin", *ADMIN_ARGS], bll=bll) == EXIT_OK
    assert Role.IT_ADMIN in next(iter(dal.users.values())).roles
    assert len(email.sent) == 1

    second = ["create-admin", "--badge", "A01-02", "--first-name", "X", "--last-name", "Y", "--email", "x@example.test"]
    assert main(second, bll=bll) == EXIT_FAILED
    assert "Un administrateur existe déjà" in capsys.readouterr().err


def test_create_user_with_several_roles() -> None:
    bll, dal, _ = _bll()
    args = ["create-user", "--badge", "B07-42", "--first-name", "Marie", "--last-name", "Joseph",
            "--email", "marie@example.test", "--role", "secretary", "--role", "trainer"]
    assert main(args, bll=bll) == EXIT_OK
    assert next(iter(dal.users.values())).roles == {Role.SECRETARY, Role.TRAINER}


def test_a_bad_badge_fails_with_a_french_message(capsys) -> None:
    bll, dal, _ = _bll()
    args = ["create-admin", *ADMIN_ARGS]
    args[args.index("A01-01")] = "A1"
    assert main(args, bll=bll) == EXIT_FAILED
    assert "A00-00" in capsys.readouterr().err
    assert dal.users == {}


def test_unblock_user_by_badge(capsys) -> None:
    bll, dal, _ = _bll()
    main(["create-admin", *ADMIN_ARGS], bll=bll)
    user = next(iter(dal.users.values()))
    dal.block(user.id, None)

    assert main(["unblock-user", "--badge", "a01-01"], bll=bll) == EXIT_OK
    assert dal.users[user.id].is_blocked is False
    assert "Compte débloqué : A01-01" in capsys.readouterr().out


def test_unblock_user_with_an_unknown_badge(capsys) -> None:
    bll, *_ = _bll()
    assert main(["unblock-user", "--badge", "Z99-99"], bll=bll) == EXIT_FAILED
    assert "Aucun compte n'a ce numéro de badge." in capsys.readouterr().err
