"""Les règles des documents de cours (US-012)."""

import uuid
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.bll.bll_document import FORMAT_REFUSED, BllDocument, check_file
from app.core.exceptions import ForbiddenError, InvalidInputError, RecordNotFoundError
from app.entities.ent_document import EntDocument
from app.entities.ent_user import EntActor, Role
from tests.unit import files
from tests.unit.fakes import actor

# --- Le contrôle des fichiers -------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "content", "content_type"),
    [
        ("Cours.pdf", files.pdf(), "application/pdf"),
        ("Cours.PDF", files.pdf(), "application/pdf"),
        ("Cours.doc", files.ole2(), "application/msword"),
        ("Cours.ppt", files.ole2(), "application/vnd.ms-powerpoint"),
        ("Cours.docx", files.docx(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        ("Cours.pptx", files.pptx(), "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
    ],
)
def test_accepted_formats(name, content, content_type) -> None:
    checked = check_file(name, content)
    assert (checked.file_name, checked.content_type) == (name, content_type)


@pytest.mark.parametrize(
    ("name", "content"),
    [
        ("faux.pdf", b"MZ\x90\x00 un programme"),
        ("faux.docx", files.pptx()),
        ("faux.pptx", files.docx()),
        ("faux.docx", b"PK pas une archive"),
        ("faux.doc", files.pdf()),
    ],
)
def test_content_must_match_the_extension(name, content) -> None:
    with pytest.raises(InvalidInputError, match="ne correspond pas"):
        check_file(name, content)


@pytest.mark.parametrize("name", ["virus.exe", "photo.jpg", "notes.txt", "sans-extension"])
def test_other_formats_are_refused(name) -> None:
    with pytest.raises(InvalidInputError, match="Format refusé"):
        check_file(name, files.pdf())
    assert "PDF" in FORMAT_REFUSED


def test_size_limits_and_empty_files() -> None:
    with pytest.raises(InvalidInputError, match="dépasse 1 Mo"):
        check_file("gros.pdf", files.pdf() + b"x" * (1024 * 1024), max_bytes=1024 * 1024)
    with pytest.raises(InvalidInputError, match="vide"):
        check_file("vide.pdf", b"")


def test_only_the_file_name_is_kept_never_a_path() -> None:
    assert check_file("C:\\Users\\admin\\Cours.pdf", files.pdf()).file_name == "Cours.pdf"
    assert check_file("../../etc/Cours.pdf", files.pdf()).file_name == "Cours.pdf"


# --- Les droits -------------------------------------------------------------------------

TRAINER_ID = uuid.uuid4()


def _doc(**overrides) -> EntDocument:
    base = EntDocument(
        id=uuid.uuid4(), module_id=uuid.uuid4(), module_title="Vitesses", training_id=uuid.uuid4(),
        training_title="Rampe", trainer_id=TRAINER_ID, file_name="Cours.pdf", content_type="application/pdf",
        size_bytes=10, uploaded_by_name="Ada Admin (Z01-01)", uploaded_at=datetime(2026, 11, 20, tzinfo=UTC),
        replaced_by_id=None, storage_name="abc",
    )
    return replace(base, **overrides)


class FakeDalDocument:
    def __init__(self, documents=(), tmp: Path | None = None) -> None:
        self.documents = {d.id: d for d in documents}
        self.added: list[tuple] = []
        self.tmp = tmp
        self.modules = {d.module_id for d in documents}

    def get(self, document_id):
        if document_id not in self.documents:
            raise RecordNotFoundError("Ce document n'existe pas.")
        return self.documents[document_id]

    def list_for_training(self, training_id):
        return [d for d in self.documents.values() if d.training_id == training_id]

    def list_all(self):
        return list(self.documents.values())

    def module_exists(self, module_id):
        return module_id in self.modules

    def add(self, module_id, new, uploaded_by, replaces=None):
        self.added.append((module_id, new.file_name, uploaded_by, replaces))
        return _doc(module_id=module_id, file_name=new.file_name)

    def path(self, document):
        path = self.tmp / document.storage_name
        path.write_bytes(b"%PDF")
        return path


def trainer(user_id=TRAINER_ID, *more: Role) -> EntActor:
    return EntActor(user_id=user_id, roles=frozenset({Role.TRAINER, *more}))


def test_the_current_trainer_and_the_admin_open_a_current_document(tmp_path) -> None:
    doc = _doc()
    bll = BllDocument(FakeDalDocument([doc], tmp_path))
    assert bll.open(trainer(), doc.id)[0] == doc
    assert bll.open(actor(Role.IT_ADMIN), doc.id)[0] == doc


@pytest.mark.parametrize("who", [trainer(uuid.uuid4()), actor(Role.COORDINATOR), actor(Role.SECRETARY), actor(Role.DIRECTION)])
def test_nobody_else_opens_a_document(tmp_path, who) -> None:
    doc = _doc()
    with pytest.raises(ForbiddenError, match="formateur du module"):
        BllDocument(FakeDalDocument([doc], tmp_path)).open(who, doc.id)


def test_a_replaced_version_is_for_the_admin_only(tmp_path) -> None:
    old = _doc(replaced_by_id=uuid.uuid4())
    bll = BllDocument(FakeDalDocument([old], tmp_path))
    with pytest.raises(ForbiddenError):
        bll.open(trainer(), old.id)
    assert bll.open(actor(Role.IT_ADMIN), old.id)[0] == old


def test_a_module_to_designate_has_no_trainer_who_opens_it(tmp_path) -> None:
    doc = _doc(trainer_id=None)
    with pytest.raises(ForbiddenError):
        BllDocument(FakeDalDocument([doc], tmp_path)).open(trainer(), doc.id)


def test_a_lost_file_says_so(tmp_path) -> None:
    doc = _doc()
    dal = FakeDalDocument([doc], tmp_path)
    dal.path = lambda document: tmp_path / "absent"
    with pytest.raises(RecordNotFoundError, match="introuvable"):
        BllDocument(dal).open(actor(Role.IT_ADMIN), doc.id)


@pytest.mark.parametrize("role", [Role.SECRETARY, Role.COORDINATOR, Role.SERVICE_HEAD, Role.DIRECTION, Role.TRAINER])
def test_only_the_admin_uploads_and_replaces(role) -> None:
    doc = _doc()
    bll = BllDocument(FakeDalDocument([doc]))
    with pytest.raises(ForbiddenError):
        bll.upload(actor(role), doc.module_id, "Cours.pdf", files.pdf())
    with pytest.raises(ForbiddenError):
        bll.replace(actor(role), doc.id, "Cours.pdf", files.pdf())


def test_the_admin_uploads_and_replaces(tmp_path) -> None:
    doc = _doc()
    dal = FakeDalDocument([doc])
    admin = actor(Role.IT_ADMIN)
    BllDocument(dal).upload(admin, doc.module_id, "Nouveau.pdf", files.pdf())
    BllDocument(dal).replace(admin, doc.id, "Cours-v2.pptx", files.pptx())
    assert dal.added == [
        (doc.module_id, "Nouveau.pdf", admin.user_id, None),
        (doc.module_id, "Cours-v2.pptx", admin.user_id, doc.id),
    ]


def test_an_unknown_module_or_an_old_version_cannot_receive_a_document() -> None:
    old = _doc(replaced_by_id=uuid.uuid4())
    bll = BllDocument(FakeDalDocument([old]))
    with pytest.raises(RecordNotFoundError):
        bll.upload(actor(Role.IT_ADMIN), uuid.uuid4(), "Cours.pdf", files.pdf())
    with pytest.raises(InvalidInputError, match="déjà été remplacé"):
        bll.replace(actor(Role.IT_ADMIN), old.id, "Cours.pdf", files.pdf())


def test_replaced_versions_are_listed_for_the_admin_only() -> None:
    training = uuid.uuid4()
    current, old = _doc(training_id=training), _doc(training_id=training, replaced_by_id=uuid.uuid4())
    bll = BllDocument(FakeDalDocument([current, old]))
    assert {d.id for d in bll.list_for_training(actor(Role.IT_ADMIN), training)} == {current.id, old.id}
    assert [d.id for d in bll.list_for_training(actor(Role.SECRETARY), training)] == [current.id]
    with pytest.raises(ForbiddenError):
        bll.list_for_training(actor(Role.TRAINER), training)
    with pytest.raises(ForbiddenError):
        bll.list_all(actor(Role.COORDINATOR))
