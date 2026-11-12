import pytest

from app.dal.database import _sqlalchemy_url


@pytest.mark.parametrize(
    "given,expected",
    [
        ("postgresql://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("postgres://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("postgresql+psycopg://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
    ],
)
def test_database_url_always_names_the_psycopg_driver(given: str, expected: str) -> None:
    assert _sqlalchemy_url(given) == expected
