from fastapi.testclient import TestClient

from app.api.v1.health import get_bll_health
from app.bll.bll_health import BllHealth
from app.main import app


class _FakeDalHealth:
    def __init__(self, is_reachable: bool) -> None:
        self._is_reachable = is_reachable

    def is_database_reachable(self) -> bool:
        return self._is_reachable


def _client_with_database(is_reachable: bool) -> TestClient:
    app.dependency_overrides[get_bll_health] = lambda: BllHealth(_FakeDalHealth(is_reachable))
    return TestClient(app)


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_health_reports_reachable_database() -> None:
    response = _client_with_database(True).get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "reachable"}


def test_health_still_answers_when_database_is_unreachable() -> None:
    response = _client_with_database(False).get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "unreachable"}


def test_health_response_carries_a_request_id() -> None:
    response = _client_with_database(True).get("/api/v1/health")

    assert response.headers["X-Request-ID"]
