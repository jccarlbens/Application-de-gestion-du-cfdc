from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

is_sqlite = settings.database_url.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}
engine = create_engine(settings.database_url, connect_args=connect_args)

# Dès l'instant où un deuxième processus ou service écrit dans le même fichier
# SQLite, le mode WAL cesse d'être facultatif — voir le piège de concurrence
# de project-docs/learnings/03-backend-layered-architecture-template.md. Le
# poser ici garantit qu'il n'est jamais absent en silence, même pour un
# service qui n'a aujourd'hui qu'un seul écrivain mais qui pourrait ne pas le
# rester.
if is_sqlite:
    @event.listens_for(engine, "connect")
    def _enable_wal_mode(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
