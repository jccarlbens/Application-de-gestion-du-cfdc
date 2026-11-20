"""« Mes modules » sur un vrai PostgreSQL (US-013) : le formateur actuel seulement,
un formateur changé, les documents en vigueur seulement."""

import uuid
from datetime import UTC, datetime

import pytest

from app.bll.bll_document import BllDocument
from app.bll.bll_training import BllTraining
from app.bll.bll_user import AccountInput, BllUser
from app.dal.dal_document import DalDocument, FileStore
from app.dal.dal_training import DalTraining
from app.dal.dal_user import DalUser
from app.entities.ent_user import EntActor, Role
from tests.unit import files
from tests.unit.fakes import FakeEmail

pytestmark = pytest.mark.integration

RAMP = uuid.UUID("0b1e0c3a-0000-4000-8000-000000000012")


def test_my_modules_follow_the_current_trainer(session_factory, tmp_path) -> None:
    users = BllUser(dal=DalUser(session_factory), email=FakeEmail(), clock=lambda: datetime(2026, 11, 20, tzinfo=UTC))

    def account(badge, role):
        return users.create_user(None, AccountInput(badge, "Prénom", badge, f"{uuid.uuid4()}@example.test", None, [role]))

    admin_user, paul_user, rose_user = account("Q31-31", "it_admin"), account("Q32-32", "trainer"), account("Q33-33", "trainer")
    admin = EntActor(user_id=admin_user.id, roles=frozenset({Role.IT_ADMIN}))
    paul = EntActor(user_id=paul_user.id, roles=frozenset({Role.TRAINER}))
    rose = EntActor(user_id=rose_user.id, roles=frozenset({Role.TRAINER}))

    dal_documents = DalDocument(session_factory, FileStore(str(tmp_path)))
    trainings = BllTraining(DalTraining(session_factory), dal_documents)
    documents = BllDocument(dal_documents)
    title = f"Rampe {uuid.uuid4().hex[:6]}"
    training = trainings.create_training(admin, title, "Pour la piste", RAMP)
    vitesses = trainings.add_module(admin, training.id, "Vitesses", None, paul_user.id)
    trainings.add_module(admin, training.id, "Balisage", None, rose_user.id)
    old = documents.upload(admin, vitesses.id, "Cours.pdf", files.pdf())
    documents.replace(admin, old.id, "Cours-v2.pdf", files.pdf())

    [mine] = [t for t in trainings.my_modules(paul) if t.title == title]
    assert [m.title for m in mine.modules] == ["Vitesses"]
    assert [d.file_name for d in mine.modules[0].documents] == ["Cours-v2.pdf"]

    # L'administrateur confie « Vitesses » à Rose : Paul le perd, Rose le gagne.
    trainings.assign_trainer(admin, vitesses.id, rose_user.id)
    assert [t for t in trainings.my_modules(paul) if t.title == title] == []
    [hers] = [t for t in trainings.my_modules(rose) if t.title == title]
    assert [m.title for m in hers.modules] == ["Vitesses", "Balisage"]
