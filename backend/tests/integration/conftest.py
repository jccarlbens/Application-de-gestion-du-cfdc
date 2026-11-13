import pytest
from sqlalchemy.orm import sessionmaker

from app.dal.database import engine


@pytest.fixture
def session_factory():
    """Une fabrique de sessions dont tout le travail est annulé à la fin du
    test : les tests d'intégration ne laissent aucun compte dans la base."""
    with engine.connect() as connection:
        transaction = connection.begin()
        yield sessionmaker(bind=connection, join_transaction_mode="create_savepoint")
        transaction.rollback()
