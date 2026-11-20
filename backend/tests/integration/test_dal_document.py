"""Les documents sur un vrai PostgreSQL et un vrai dossier (US-012) : dépôt,
remplacement, aucun fichier orphelin, journal dans l'historique de la formation."""

import uuid
from datetime import UTC, datetime

import pytest

from app.bll.bll_document import BllDocument
from app.bll.bll_history import BllHistory
from app.bll.bll_training import BllTraining
from app.bll.bll_user import AccountInput, BllUser, audit_actor
from app.core.exceptions import RecordNotFoundError
from app.dal.dal_audit import DalAudit, acting_as
from app.dal.dal_document import DalDocument, FileStore
from app.dal.dal_training import DalTraining
from app.dal.dal_user import DalUser
from app.entities.ent_document import EntNewDocument
from app.entities.ent_user import EntActor, Role
from tests.unit import files
from tests.unit.fakes import FakeEmail

pytestmark = pytest.mark.integration

RAMP = uuid.UUID("0b1e0c3a-0000-4000-8000-000000000012")


@pytest.fixture
def setup(session_factory, tmp_path):
    users = BllUser(dal=DalUser(session_factory), email=FakeEmail(), clock=lambda: datetime(2026, 11, 20, tzinfo=UTC))
    admin = users.create_user(None, AccountInput("Q21-21", "Ada", "Admin", f"{uuid.uuid4()}@example.test", None, ["it_admin"]))
    paul = users.create_user(None, AccountInput("Q22-22", "Paul", "Michel", f"{uuid.uuid4()}@example.test", None, ["trainer"]))
    as_admin = EntActor(user_id=admin.id, roles=frozenset({Role.IT_ADMIN}))
    trainings = BllTraining(DalTraining(session_factory))
    training = trainings.create_training(as_admin, f"Rampe {uuid.uuid4().hex[:6]}", None, RAMP)
    module = trainings.add_module(as_admin, training.id, "Vitesses", None, paul.id)
    dal = DalDocument(session_factory, FileStore(str(tmp_path / "documents")))
    return {
        "bll": BllDocument(dal), "dal": dal, "dir": tmp_path / "documents", "admin": as_admin,
        "paul": EntActor(user_id=paul.id, roles=frozenset({Role.TRAINER})), "training": training, "module": module,
        "history": BllHistory(DalAudit(session_factory)),
    }


def test_upload_replace_and_open(setup) -> None:
    s = setup
    first = s["bll"].upload(s["admin"], s["module"].id, "Cours.pdf", files.pdf())
    assert (first.uploaded_by_name, first.module_title, first.trainer_id) == ("Ada Admin (Q21-21)", "Vitesses", s["module"].trainer.id)
    second = s["bll"].replace(s["admin"], first.id, "Cours-v2.pptx", files.pptx())

    listed = s["bll"].list_for_training(s["admin"], s["training"].id)
    assert [(d.file_name, d.replaced_by_id) for d in listed] == [("Cours.pdf", second.id), ("Cours-v2.pptx", None)]
    _, path = s["bll"].open(s["paul"], second.id)
    assert path.read_bytes() == files.pptx()
    # Deux fichiers sur le disque, sous des noms aléatoires ; aucun temporaire.
    assert sorted(p.name for p in s["dir"].iterdir()) == sorted([first.storage_name, second.storage_name])


def test_uploads_are_told_in_the_history_of_the_training(setup) -> None:
    s = setup
    first = s["bll"].upload(s["admin"], s["module"].id, "Cours.pdf", files.pdf())
    s["bll"].replace(s["admin"], first.id, "Cours-v2.pdf", files.pdf())
    entries = [e for e in s["history"].history(s["admin"], "trainings", str(s["training"].id)) if e.table_name == "course_documents"]
    assert [(e.action.value, (e.after or {}).get("file_name")) for e in entries] == [
        ("create", "Cours.pdf"),
        ("create", "Cours-v2.pdf"),
        ("update", "Cours.pdf"),
    ]
    assert entries[2].after["replaced_by_id"] is not None
    assert {e.actor_name for e in entries} == {"Ada Admin (Q21-21)"}


def test_no_orphan_file_when_the_record_cannot_be_saved(setup) -> None:
    s = setup
    with pytest.raises(RecordNotFoundError):
        with acting_as(audit_actor(s["admin"])):
            s["dal"].add(uuid.uuid4(), EntNewDocument("Cours.pdf", "application/pdf", files.pdf()), s["admin"].user_id)
    assert list(s["dir"].iterdir()) == []
