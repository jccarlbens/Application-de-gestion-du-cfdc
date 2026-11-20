"""Les règles du catalogue des formations (US-010)."""

import uuid

import pytest

from app.bll.bll_training import BllTraining, title_key
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


def _create(bll, dal, title="Conduite sur la rampe — niveau 1", who=Role.SECRETARY, description=None):
    return bll.create_training(actor(who), title, description, dal.subdomain_id("Conduite sur la rampe"))


def test_the_title_key_ignores_case_and_extra_spaces_but_not_accents() -> None:
    assert title_key("  Conduite   sur la RAMPE ") == title_key("conduite sur la rampe")
    assert title_key("Sûreté") != title_key("Surete")


@pytest.mark.parametrize("role", WRITERS)
def test_these_roles_record_a_training(bll, dal, role) -> None:
    training = _create(bll, dal, who=role)
    assert training.domain_name == "Sûreté-Sécurité"
    assert training.subdomain_name == "Conduite sur la rampe"


@pytest.mark.parametrize("role", [Role.DIRECTION, Role.TRAINER])
def test_direction_and_trainers_do_not_record_a_training(bll, dal, role) -> None:
    with pytest.raises(ForbiddenError):
        _create(bll, dal, who=role)


def test_the_title_is_cleaned_and_the_empty_description_dropped(bll, dal) -> None:
    training = _create(bll, dal, title="  Conduite   sur la rampe  ", description="   ")
    assert training.title == "Conduite sur la rampe"
    assert training.description is None


def test_a_title_already_taken_with_other_case_or_spaces_is_refused(bll, dal) -> None:
    _create(bll, dal, title="Conduite sur la rampe")
    with pytest.raises(DuplicateNameError, match="déjà cet intitulé"):
        _create(bll, dal, title="CONDUITE  sur la rampe ")


@pytest.mark.parametrize(
    ("title", "description", "message"),
    [
        ("   ", None, "obligatoire"),
        ("x" * 201, None, "200 caractères"),
        ("Protocole", "y" * 2001, "2000 caractères"),
    ],
)
def test_limits_are_checked_in_french(bll, dal, title, description, message) -> None:
    with pytest.raises(InvalidInputError, match=message):
        _create(bll, dal, title=title, description=description)


def test_an_unknown_subdomain_is_refused(bll) -> None:
    with pytest.raises(InvalidInputError, match="sous-domaine"):
        bll.create_training(actor(Role.SECRETARY), "Protocole", None, uuid.uuid4())


def test_trainers_do_not_see_the_catalogue(bll) -> None:
    with pytest.raises(ForbiddenError):
        bll.list_trainings(actor(Role.TRAINER))
    with pytest.raises(ForbiddenError):
        bll.list_domains(actor(Role.TRAINER))


def test_the_catalogue_is_sorted_by_domain_subdomain_then_title(bll, dal) -> None:
    bll.create_training(actor(Role.SECRETARY), "Zèle", None, dal.subdomain_id("Protocole"))
    bll.create_training(actor(Role.SECRETARY), "Accueil VIP", None, dal.subdomain_id("Protocole"))
    _create(bll, dal, title="Rampe")
    titles = [t.title for t in bll.list_trainings(actor(Role.DIRECTION))]
    assert titles == ["Accueil VIP", "Zèle", "Rampe"]


def test_only_the_admin_updates_a_training(bll, dal) -> None:
    training = _create(bll, dal)
    for role in [Role.SECRETARY, Role.COORDINATOR, Role.SERVICE_HEAD]:
        with pytest.raises(ForbiddenError, match="demande de correction"):
            bll.update_training(actor(role), training.id, "Autre", None, training.subdomain_id)
    updated = bll.update_training(actor(Role.IT_ADMIN), training.id, "Autre", "Texte", dal.subdomain_id("Civilité"))
    assert (updated.title, updated.description, updated.domain_name) == ("Autre", "Texte", "Accueil")


def test_the_admin_may_keep_the_same_title_with_another_case(bll, dal) -> None:
    training = _create(bll, dal, title="Protocole")
    assert bll.update_training(actor(Role.IT_ADMIN), training.id, "PROTOCOLE", None, training.subdomain_id).title == "PROTOCOLE"


def test_updating_an_unknown_training_says_so(bll, dal) -> None:
    with pytest.raises(RecordNotFoundError):
        bll.update_training(actor(Role.IT_ADMIN), uuid.uuid4(), "X", None, dal.subdomain_id("Protocole"))


# --- Domaines et sous-domaines ---------------------------------------------------


def test_only_the_admin_manages_domains(bll, dal) -> None:
    for role in [Role.SECRETARY, Role.COORDINATOR, Role.SERVICE_HEAD, Role.DIRECTION]:
        with pytest.raises(ForbiddenError):
            bll.add_domain(actor(role), "Exploitation")
        with pytest.raises(ForbiddenError):
            bll.rename_subdomain(actor(role), dal.subdomain_id("Protocole"), "Protocole d'État")


def test_the_admin_adds_and_renames_domains_and_subdomains(bll, dal) -> None:
    admin = actor(Role.IT_ADMIN)
    domain = bll.add_domain(admin, "  Exploitation ")
    assert domain.name == "Exploitation"
    sub = bll.add_subdomain(admin, domain.id, "Balisage")
    assert bll.rename_subdomain(admin, sub.id, "Balisage lumineux").name == "Balisage lumineux"
    assert bll.rename_domain(admin, domain.id, "Exploitation aéroportuaire").name == "Exploitation aéroportuaire"


def test_names_already_taken_are_refused_whatever_the_case(bll, dal) -> None:
    admin = actor(Role.IT_ADMIN)
    with pytest.raises(DuplicateNameError, match="domaine"):
        bll.add_domain(admin, "ACCUEIL")
    with pytest.raises(DuplicateNameError, match="sous-domaine"):
        bll.add_subdomain(admin, dal.domain_id("Accueil"), "civilité")
    with pytest.raises(DuplicateNameError):
        bll.rename_subdomain(admin, dal.subdomain_id("Protocole"), "Civilité")
    with pytest.raises(DuplicateNameError):
        bll.rename_domain(admin, dal.domain_id("Accueil"), "Sûreté-Sécurité")


def test_a_subdomain_name_may_repeat_in_another_domain(bll, dal) -> None:
    sub = bll.add_subdomain(actor(Role.IT_ADMIN), dal.domain_id("Accueil"), "Conduite sur la rampe")
    assert sub.name == "Conduite sur la rampe"


def test_renaming_with_another_case_of_its_own_name_is_allowed(bll, dal) -> None:
    assert bll.rename_domain(actor(Role.IT_ADMIN), dal.domain_id("Accueil"), "ACCUEIL").name == "ACCUEIL"


def test_empty_or_too_long_names_are_refused(bll, dal) -> None:
    with pytest.raises(InvalidInputError, match="obligatoire"):
        bll.add_domain(actor(Role.IT_ADMIN), "  ")
    with pytest.raises(InvalidInputError, match="100 caractères"):
        bll.add_subdomain(actor(Role.IT_ADMIN), dal.domain_id("Accueil"), "z" * 101)


def test_unknown_domains_and_subdomains_say_so(bll) -> None:
    with pytest.raises(RecordNotFoundError):
        bll.add_subdomain(actor(Role.IT_ADMIN), uuid.uuid4(), "X")
    with pytest.raises(RecordNotFoundError):
        bll.rename_subdomain(actor(Role.IT_ADMIN), uuid.uuid4(), "X")
