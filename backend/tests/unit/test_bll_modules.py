"""Les règles des modules et de leurs formateurs (US-011)."""

import uuid

import pytest

from app.bll.bll_training import BllTraining
from app.core.exceptions import DuplicateNameError, ForbiddenError, InvalidInputError, RecordNotFoundError
from app.entities.ent_user import Role
from tests.unit.fakes import FakeDalTraining, actor

WRITERS = [Role.SECRETARY, Role.COORDINATOR, Role.SERVICE_HEAD, Role.IT_ADMIN]


@pytest.fixture
def dal() -> FakeDalTraining:
    return FakeDalTraining()


@pytest.fixture
def bll(dal) -> BllTraining:
    return BllTraining(dal)


@pytest.fixture
def training(bll, dal):
    return bll.create_training(actor(Role.SECRETARY), "Conduite sur la rampe", None, dal.subdomain_id("Conduite sur la rampe"))


@pytest.fixture
def paul(dal):
    return dal.add_trainer("Paul", "Michel", "C03-15")


@pytest.fixture
def rose(dal):
    return dal.add_trainer("Rose", "Pierre", "E05-55")


@pytest.mark.parametrize("role", WRITERS)
def test_these_roles_add_a_module_with_or_without_trainer(bll, training, paul, role) -> None:
    with_trainer = bll.add_module(actor(role), training.id, "  Signalisation   au sol ", None, paul.id)
    assert with_trainer.title == "Signalisation au sol"
    assert with_trainer.trainer.badge == "C03-15"
    assert bll.add_module(actor(role), training.id, "Vitesses", " ", None).trainer is None


@pytest.mark.parametrize("role", [Role.DIRECTION, Role.TRAINER])
def test_direction_and_trainers_do_not_add_modules(bll, training, role) -> None:
    with pytest.raises(ForbiddenError):
        bll.add_module(actor(role), training.id, "Vitesses", None, None)


def test_a_title_is_unique_in_its_training_only(bll, dal, training) -> None:
    bll.add_module(actor(Role.SECRETARY), training.id, "Vitesses", None, None)
    with pytest.raises(DuplicateNameError, match="déjà un module de ce titre"):
        bll.add_module(actor(Role.SECRETARY), training.id, " VITESSES ", None, None)
    other = bll.create_training(actor(Role.SECRETARY), "Protocole", None, dal.subdomain_id("Protocole"))
    assert bll.add_module(actor(Role.SECRETARY), other.id, "Vitesses", None, None).title == "Vitesses"


@pytest.mark.parametrize(
    ("title", "description", "message"),
    [("  ", None, "obligatoire"), ("t" * 201, None, "200 caractères"), ("Vitesses", "d" * 2001, "2000 caractères")],
)
def test_limits_are_checked_in_french(bll, training, title, description, message) -> None:
    with pytest.raises(InvalidInputError, match=message):
        bll.add_module(actor(Role.SECRETARY), training.id, title, description, None)


def test_a_module_needs_an_existing_training(bll) -> None:
    with pytest.raises(RecordNotFoundError):
        bll.add_module(actor(Role.SECRETARY), uuid.uuid4(), "Vitesses", None, None)


def test_the_trainer_must_be_an_active_trainer(bll, dal, training) -> None:
    gone = dal.add_trainer("Jean", "Absent", "J01-01", is_active=False)
    not_trainer = dal.add_trainer("Léa", "Secrétaire", "L01-01", is_trainer=False)
    with pytest.raises(InvalidInputError, match="désactivé"):
        bll.add_module(actor(Role.SECRETARY), training.id, "A", None, gone.id)
    with pytest.raises(InvalidInputError, match="rôle de formateur"):
        bll.add_module(actor(Role.SECRETARY), training.id, "B", None, not_trainer.id)
    with pytest.raises(InvalidInputError, match="rôle de formateur"):
        bll.add_module(actor(Role.SECRETARY), training.id, "C", None, uuid.uuid4())


@pytest.mark.parametrize("role", WRITERS)
def test_these_roles_assign_the_trainer_of_a_module_to_designate(bll, training, paul, role) -> None:
    module = bll.add_module(actor(Role.SECRETARY), training.id, "Vitesses", None, None)
    assert bll.assign_trainer(actor(role), module.id, paul.id).trainer.id == paul.id


@pytest.mark.parametrize("role", [Role.SECRETARY, Role.COORDINATOR, Role.SERVICE_HEAD])
def test_only_the_admin_changes_a_trainer_already_designated(bll, training, paul, rose, role) -> None:
    module = bll.add_module(actor(Role.SECRETARY), training.id, "Vitesses", None, paul.id)
    with pytest.raises(ForbiddenError, match="seul l'administrateur"):
        bll.assign_trainer(actor(role), module.id, rose.id)
    assert bll.assign_trainer(actor(Role.IT_ADMIN), module.id, rose.id).trainer.id == rose.id


def test_trainers_are_listed_for_writers_only_and_without_inactive_ones(bll, dal, paul, rose) -> None:
    dal.add_trainer("Jean", "Absent", "J01-01", is_active=False)
    assert [t.badge for t in bll.list_trainers(actor(Role.SECRETARY))] == ["C03-15", "E05-55"]
    with pytest.raises(ForbiddenError):
        bll.list_trainers(actor(Role.DIRECTION))


def test_modules_are_listed_for_readers_in_the_order_they_were_added(bll, training) -> None:
    for title in ["Vitesses", "Annonces", "Balisage"]:
        bll.add_module(actor(Role.SECRETARY), training.id, title, None, None)
    assert [m.title for m in bll.list_modules(actor(Role.DIRECTION), training.id)] == ["Vitesses", "Annonces", "Balisage"]
    with pytest.raises(ForbiddenError):
        bll.list_modules(actor(Role.TRAINER), training.id)
    with pytest.raises(RecordNotFoundError):
        bll.list_modules(actor(Role.DIRECTION), uuid.uuid4())


def test_only_the_admin_updates_a_module(bll, training, paul) -> None:
    module = bll.add_module(actor(Role.SECRETARY), training.id, "Vitesses", None, None)
    for role in [Role.SECRETARY, Role.COORDINATOR, Role.SERVICE_HEAD]:
        with pytest.raises(ForbiddenError, match="demande de correction"):
            bll.update_module(actor(role), module.id, "Autre", None, None)
    updated = bll.update_module(actor(Role.IT_ADMIN), module.id, "Vitesses sur la rampe", "Texte", paul.id)
    assert (updated.title, updated.description, updated.trainer.id) == ("Vitesses sur la rampe", "Texte", paul.id)


def test_the_admin_may_keep_a_trainer_who_left_the_role(bll, dal, training, paul) -> None:
    module = bll.add_module(actor(Role.SECRETARY), training.id, "Vitesses", None, paul.id)
    dal.trainers[paul.id] = type(paul)(paul.id, "Paul", "Michel", "C03-15", False, True)
    # Décision 4A : le module garde son formateur désactivé ; on peut corriger le titre.
    assert bll.update_module(actor(Role.IT_ADMIN), module.id, "Vitesse", None, paul.id).trainer.is_active is False


def test_the_admin_may_set_a_module_back_to_designate(bll, training, paul) -> None:
    module = bll.add_module(actor(Role.SECRETARY), training.id, "Vitesses", None, paul.id)
    assert bll.update_module(actor(Role.IT_ADMIN), module.id, "Vitesses", None, None).trainer is None
