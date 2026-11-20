"""Les documents de cours (US-012) : les fichiers sur le disque du serveur
(ADR 4), et leur fiche dans `course_documents`, journalisée sous la formation.

Un fichier est rangé sous un nom aléatoire, jamais sous le nom donné par
l'utilisateur. Il est écrit avant la fiche ; si la fiche ne s'enregistre pas,
le fichier est effacé : pas de fichier orphelin. Rien ne s'efface ensuite :
remplacer un document en ajoute un nouveau et garde l'ancien.
"""

import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship, sessionmaker

from app.core.config import settings
from app.core.exceptions import RecordNotFoundError
from app.dal.dal_audit import AuditPolicy
from app.dal.dal_training import ModuleModel, TrainingModel
from app.dal.dal_user import UserModel
from app.dal.database import Base, SessionLocal
from app.entities.ent_document import EntDocument, EntNewDocument


class CourseDocumentModel(Base):
    __tablename__ = "course_documents"
    # Dans l'historique de la formation, comme les modules (US-012, décision 5A).
    __audit__ = AuditPolicy(subject=lambda doc: ("trainings", doc.module.training_id))

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    module_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("modules.id"), index=True)
    file_name: Mapped[str] = mapped_column(String(200))
    content_type: Mapped[str] = mapped_column(String(120))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    # Le nom du fichier sur le disque, aléatoire.
    storage_name: Mapped[str] = mapped_column(String(64), unique=True)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    # clock_timestamp() : l'ordre des dépôts, même dans une seule transaction.
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.clock_timestamp())
    replaced_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("course_documents.id"))

    module: Mapped[ModuleModel] = relationship(lazy="joined")


class FileStore:
    """Le dossier des documents (DOCUMENTS_DIR)."""

    def __init__(self, directory: str | None = None) -> None:
        self._dir = Path(directory or settings.documents_dir)

    def path(self, storage_name: str) -> Path:
        return self._dir / storage_name

    def save(self, content: bytes) -> str:
        """Écrit d'abord un fichier temporaire, puis le met à sa place : un
        fichier à moitié écrit ne porte jamais un nom de document."""
        self._dir.mkdir(parents=True, exist_ok=True)
        storage_name = uuid.uuid4().hex
        fd, tmp = tempfile.mkstemp(dir=self._dir, prefix=".upload-")
        try:
            with os.fdopen(fd, "wb") as out:
                out.write(content)
            os.replace(tmp, self.path(storage_name))
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise
        return storage_name

    def delete(self, storage_name: str) -> None:
        self.path(storage_name).unlink(missing_ok=True)


def _select():
    uploader = (UserModel.first_name + " " + UserModel.last_name + " (" + UserModel.badge + ")").label("uploader")
    return (
        select(CourseDocumentModel, ModuleModel, TrainingModel, uploader)
        .join(ModuleModel, ModuleModel.id == CourseDocumentModel.module_id)
        .join(TrainingModel, TrainingModel.id == ModuleModel.training_id)
        .join(UserModel, UserModel.id == CourseDocumentModel.uploaded_by)
    )


def _entity(doc: CourseDocumentModel, module: ModuleModel, training: TrainingModel, uploader: str) -> EntDocument:
    return EntDocument(
        id=doc.id,
        module_id=module.id,
        module_title=module.title,
        training_id=training.id,
        training_title=training.title,
        trainer_id=module.trainer_id,
        file_name=doc.file_name,
        content_type=doc.content_type,
        size_bytes=doc.size_bytes,
        uploaded_by_name=uploader,
        uploaded_at=doc.uploaded_at,
        replaced_by_id=doc.replaced_by_id,
        storage_name=doc.storage_name,
    )


class DalDocument:
    def __init__(self, session_factory: sessionmaker[Session] = SessionLocal, files: FileStore | None = None) -> None:
        self._sessions = session_factory
        self._files = files or FileStore()

    def path(self, document: EntDocument) -> Path:
        return self._files.path(document.storage_name)

    def get(self, document_id: uuid.UUID) -> EntDocument:
        with self._sessions() as session:
            row = session.execute(_select().where(CourseDocumentModel.id == document_id)).one_or_none()
            if row is None:
                raise RecordNotFoundError("Ce document n'existe pas.")
            return _entity(*row)

    def list_for_training(self, training_id: uuid.UUID) -> list[EntDocument]:
        with self._sessions() as session:
            rows = session.execute(
                _select()
                .where(ModuleModel.training_id == training_id)
                .order_by(ModuleModel.created_at, CourseDocumentModel.uploaded_at)
            )
            return [_entity(*row) for row in rows]

    def list_all(self) -> list[EntDocument]:
        with self._sessions() as session:
            rows = session.execute(
                _select().order_by(TrainingModel.title, ModuleModel.created_at, CourseDocumentModel.uploaded_at)
            )
            return [_entity(*row) for row in rows]

    def module_exists(self, module_id: uuid.UUID) -> bool:
        with self._sessions() as session:
            return session.get(ModuleModel, module_id) is not None

    def add(self, module_id: uuid.UUID, new: EntNewDocument, uploaded_by: uuid.UUID, replaces: uuid.UUID | None = None):
        """Range le fichier, puis enregistre sa fiche ; `replaces` marque, dans
        la même transaction, l'ancienne version comme remplacée."""
        storage_name = self._files.save(new.content)
        try:
            with self._sessions() as session:
                module = session.get(ModuleModel, module_id)
                if module is None:
                    raise RecordNotFoundError("Ce module n'existe pas.")
                doc = CourseDocumentModel(
                    module=module,
                    file_name=new.file_name,
                    content_type=new.content_type,
                    size_bytes=len(new.content),
                    storage_name=storage_name,
                    uploaded_by=uploaded_by,
                )
                session.add(doc)
                session.flush()
                if replaces is not None:
                    old = session.get(CourseDocumentModel, replaces)
                    old.replaced_by_id = doc.id
                session.commit()
                document_id = doc.id
        except BaseException:
            self._files.delete(storage_name)
            raise
        return self.get(document_id)
