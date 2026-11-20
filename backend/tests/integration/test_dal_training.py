"""Le catalogue sur un vrai PostgreSQL (US-010) : la liste de départ, les
contraintes d'unicité, et le journal des trois tables avec le nom de l'auteur."""

import uuid

import pytest
from sqlalchemy import text

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
PROTOCOL = uuid.UUID("0b1e0c3a-0000-4000-8000-000000000021")


@pytest.fixture
def setup(session_factory):
    # Un administrateur réel, pour que le journal puisse le nommer.
    users = BllUser(dal=DalUser(session_factory), email=FakeEmail())
    admin = users.create_user(None, AccountInput("Q42-42", "Ada", "Admin", f"{uuid.uuid4()}@example.test", None, ["it_admin"]))
    actor = EntActor(user_id=admin.id, roles=frozenset({Role.IT_ADMIN}))
    return BllTraining(DalTraining(session_factory)), BllHistory(DalAudit(session_factory)), actor, session_factory


def test_the_starting_list_is_there(setup) -> None:
    bll, _, actor, _ = setup
    domains = {d.name: [s.name for s in d.subdomains] for d in bll.list_domains(actor)}
    assert domains["Sûreté-Sécurité"] == [
        "Conduite sur la rampe",
        "Formation des policiers",
        "Sensibilisation sur la carte d'accès",
    ]
    assert domains["Accueil"] == ["Civilité", "Protocole"]


def test_a_training_is_recorded_updated_and_logged_with_its_author(setup) -> None:
    bll, history, actor, _ = setup
    title = f"Rampe {uuid.uuid4().hex[:6]}"
    training = bll.create_training(actor, title, None, RAMP)
    updated = bll.update_training(actor, training.id, title + " bis", "Pour les chauffeurs", PROTOCOL)
    # Le classement suit le changement de sous-domaine.
    assert (updated.subdomain_name, updated.domain_name) == ("Protocole", "Accueil")

    entries = history.history(actor, "trainings", str(training.id))
    assert [e.action.value for e in entries] == ["create", "update"]
    assert {e.actor_name for e in entries} == {"Ada Admin (Q42-42)"}
    assert entries[1].after["title"] == title + " bis"
    assert entries[1].before["subdomain_id"] == str(RAMP)


def test_the_database_refuses_a_duplicate_title_key(setup) -> None:
    bll, _, actor, _ = setup
    title = f"Doublon {uuid.uuid4().hex[:6]}"
    bll.create_training(actor, title, None, RAMP)
    # La BLL ne vérifie pas d'avance : c'est la contrainte de la base qui parle.
    with pytest.raises(DuplicateNameError, match="déjà cet intitulé"):
        bll.create_training(actor, title.upper(), None, PROTOCOL)


def test_domains_and_subdomains_are_added_renamed_and_logged(setup) -> None:
    bll, history, actor, _ = setup
    name = f"Exploitation {uuid.uuid4().hex[:6]}"
    domain = bll.add_domain(actor, name)
    sub = bll.add_subdomain(actor, domain.id, "Balisage")
    bll.rename_subdomain(actor, sub.id, "Balisage lumineux")
    assert [e.action.value for e in history.history(actor, "domains", str(domain.id))] == ["create"]
    entries = history.history(actor, "subdomains", str(sub.id))
    assert [e.action.value for e in entries] == ["create", "update"]
    assert entries[1].after["name"] == "Balisage lumineux"


def test_the_starting_list_has_no_journal_entries(setup) -> None:
    _, history, actor, _ = setup
    # Chargée par la migration (US-010, décision 5) : l'écran dira « Chargé à l'installation ».
    assert history.history(actor, "subdomains", str(PROTOCOL)) == []


def test_a_command_line_entry_has_no_author_name(setup) -> None:
    _, history, actor, session_factory = setup
    with session_factory() as session:
        user_id = session.scalar(text("SELECT id FROM users WHERE badge = 'Q42-42'"))
    entries = history.history(EntActor(user_id=user_id, roles=frozenset({Role.IT_ADMIN})), "users", str(user_id))
    assert entries[0].actor_name is None
    assert entries[0].actor_label == "Ligne de commande (administrateur)"
