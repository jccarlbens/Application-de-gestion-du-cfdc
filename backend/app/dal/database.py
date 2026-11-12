from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


def _sqlalchemy_url(url: str) -> str:
    """Neon et Render donnent une adresse `postgresql://` ; SQLAlchemy a
    besoin du nom du pilote (`psycopg`, version 3)."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


# pool_pre_ping : le serveur de test (Render et Neon) s'endort ; une connexion
# restée dans le pool peut être morte au réveil.
engine = create_engine(_sqlalchemy_url(settings.database_url), pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
