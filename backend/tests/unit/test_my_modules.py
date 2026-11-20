"""« Mes modules » du formateur (US-013)."""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.api.v1.security import get_current_actor
from app.api.v1.trainings import get_bll_training
from app.bll.bll_training import BllTraining
from app.core.exceptions import ForbiddenError
from app.entities.ent_user import EntActor, Role
from app.main import app
from tests.unit.fakes import FakeDalTraining, actor
from tests.unit.test_bll_document import _doc


class FakeDocuments:
    def __init__(self, documents) -> None:
        self.documents = documents

    def list_current_for_modules(self, module_ids):
        return [d for d in self.documents if d.module_id in module_ids and d.is_current]


@pytest.fixture
def world():
    dal = FakeDalTraining()
    paul, rose = dal.add_trainer("Paul", "Michel", "C03-15"), dal.add_trainer("Rose", "Pierre", "E05-55")
    sec = actor(Role.SECRETARY)
    bll0 = BllTraining(dal, FakeDocuments([]))
    ramp = bll0.create_training(sec, "Rampe", "Pour la piste", dal.subdomain_id("Conduite sur la rampe"))
    welcome = bll0.create_training(sec, "Accueil VIP", None, dal.subdomain_id("Protocole"))
    m1 = bll0.add_module(sec, ramp.id, "Vitesses", None, paul.id)
    m2 = bll0.add_module(sec, ramp.id, "Balisage", "Les feux", paul.id)
    bll0.add_module(sec, ramp.id, "Annonces", None, rose.id)
    bll0.add_module(sec, ramp.id, "À voir", None, None)
    m3 = bll0.add_module(sec, welcome.id, "Salutations", None, paul.id)
    docs = [
        _doc(module_id=m1.id, file_name="Vitesses.pdf"),
        _doc(module_id=m1.id, file_name="Ancien.pdf", replaced_by_id=uuid.uuid4()),
        _doc(module_id=m3.id, file_name="Accueil.pptx"),
    ]
    return {"bll": BllTraining(dal, FakeDocuments(docs)), "paul": paul, "rose": rose, "m2": m2}


def _as_trainer(trainer, *more: Role) -> EntActor:
    return EntActor(user_id=trainer.id, roles=frozenset({Role.TRAINER, *more}))


def test_a_trainer_sees_only_his_modules_by_training_with_current_documents(world) -> None:
    mine = world["bll"].my_modules(_as_trainer(world["paul"]))
    assert [t.title for t in mine] == ["Accueil VIP", "Rampe"]
    ramp = mine[1]
    assert (ramp.description, ramp.domain_name, ramp.subdomain_name) == ("Pour la piste", "Sûreté-Sécurité", "Conduite sur la rampe")
    assert [m.title for m in ramp.modules] == ["Vitesses", "Balisage"]
    assert [d.file_name for d in ramp.modules[0].documents] == ["Vitesses.pdf"]
    assert ramp.modules[1].description == "Les feux"
    assert ramp.modules[1].documents == ()


def test_another_trainer_sees_his_own_only(world) -> None:
    mine = world["bll"].my_modules(_as_trainer(world["rose"]))
    assert [(t.title, [m.title for m in t.modules]) for t in mine] == [("Rampe", ["Annonces"])]


def test_a_trainer_without_modules_gets_an_empty_list(world) -> None:
    assert world["bll"].my_modules(EntActor(user_id=uuid.uuid4(), roles=frozenset({Role.TRAINER}))) == []


@pytest.mark.parametrize("role", [Role.SECRETARY, Role.COORDINATOR, Role.SERVICE_HEAD, Role.IT_ADMIN, Role.DIRECTION])
def test_other_roles_have_no_my_modules(world, role) -> None:
    with pytest.raises(ForbiddenError, match="réservée aux formateurs"):
        world["bll"].my_modules(actor(role))


def test_the_route_serves_the_connected_trainer_without_uploader(world) -> None:
    app.dependency_overrides[get_bll_training] = lambda: world["bll"]
    app.dependency_overrides[get_current_actor] = lambda: _as_trainer(world["paul"])
    try:
        body = TestClient(app).get("/api/v1/me/modules").json()
    finally:
        app.dependency_overrides.clear()
    assert [t["title"] for t in body] == ["Accueil VIP", "Rampe"]
    document = body[1]["modules"][0]["documents"][0]
    assert set(document) == {"id", "file_name", "size_bytes", "uploaded_at"}
