"""Les routes des documents de cours (US-012)."""

import pytest
from fastapi.testclient import TestClient

from app.api.v1.documents import get_bll_document
from app.api.v1.security import get_current_actor
from app.bll.bll_document import BllDocument
from app.entities.ent_user import Role
from app.main import app
from tests.unit import files
from tests.unit.fakes import actor
from tests.unit.test_bll_document import FakeDalDocument, _doc, trainer


@pytest.fixture
def doc():
    return _doc(file_name="Cours d'été.pdf")


@pytest.fixture
def client(doc, tmp_path):
    dal = FakeDalDocument([doc], tmp_path)
    app.dependency_overrides[get_bll_document] = lambda: BllDocument(dal)
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_the_admin_uploads_a_file(client, doc) -> None:
    app.dependency_overrides[get_current_actor] = lambda: actor(Role.IT_ADMIN)
    response = client.post(f"/api/v1/modules/{doc.module_id}/documents", files={"file": ("Cours.pdf", files.pdf(), "application/pdf")})
    assert response.status_code == 201
    assert response.json()["file_name"] == "Cours.pdf"
    assert "storage_name" not in response.json()


def test_a_wrong_format_answers_422_in_french(client, doc) -> None:
    app.dependency_overrides[get_current_actor] = lambda: actor(Role.IT_ADMIN)
    response = client.post(f"/api/v1/modules/{doc.module_id}/documents", files={"file": ("image.png", b"\x89PNG", "image/png")})
    assert response.status_code == 422
    assert response.json()["detail"].startswith("Format refusé")


def test_the_trainer_downloads_with_the_original_name(client, doc) -> None:
    app.dependency_overrides[get_current_actor] = lambda: trainer()
    response = client.get(f"/api/v1/documents/{doc.id}/download")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    assert "filename*=utf-8''Cours%20d%27%C3%A9t%C3%A9.pdf" in response.headers["content-disposition"]


@pytest.mark.parametrize("role", [Role.SECRETARY, Role.COORDINATOR, Role.SERVICE_HEAD, Role.DIRECTION])
def test_other_roles_are_refused_the_download_by_the_route(client, doc, role) -> None:
    app.dependency_overrides[get_current_actor] = lambda: actor(role)
    assert client.get(f"/api/v1/documents/{doc.id}/download").status_code == 403
