"""Les sessions de formation (US-015), journalisées. Le nom `training_sessions`
évite l'homonyme avec les sessions de connexion (`auth_sessions`)."""

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from app.core.exceptions import RecordNotFoundError
from app.dal.dal_audit import AuditPolicy
from app.dal.dal_training import TrainingModel
from app.dal.dal_training_request import TrainingRequestModel
from app.dal.dal_user import UserModel
from app.dal.database import Base, SessionLocal
from app.entities.ent_training_session import EntTrainingSession, SessionStatus


class TrainingSessionModel(Base):
    __tablename__ = "training_sessions"
    __audit__ = AuditPolicy(subject=lambda s: ("training_sessions", s.id))

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    training_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trainings.id"), index=True)
    request_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("training_requests.id"), index=True)
    label: Mapped[str | None] = mapped_column(String(100))
    # Des dates du calendrier de l'AAN, sans fuseau (SOLUTION_DESIGN.md §6).
    starts_on: Mapped[date] = mapped_column(Date, index=True)
    ends_on: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(10), default=SessionStatus.PLANNED.value)
    cancel_reason: Mapped[str | None] = mapped_column(String(2000))
    planned_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.clock_timestamp())


def _select():
    planner = (UserModel.first_name + " " + UserModel.last_name + " (" + UserModel.badge + ")").label("planner")
    return (
        select(TrainingSessionModel, TrainingModel.title, TrainingRequestModel.requesting_service, planner)
        .join(TrainingModel, TrainingModel.id == TrainingSessionModel.training_id)
        .join(UserModel, UserModel.id == TrainingSessionModel.planned_by)
        .outerjoin(TrainingRequestModel, TrainingRequestModel.id == TrainingSessionModel.request_id)
    )


def _entity(model: TrainingSessionModel, title: str, service: str | None, planner: str) -> EntTrainingSession:
    return EntTrainingSession(
        id=model.id,
        training_id=model.training_id,
        training_title=title,
        request_id=model.request_id,
        request_service=service,
        label=model.label,
        starts_on=model.starts_on,
        ends_on=model.ends_on,
        status=SessionStatus(model.status),
        cancel_reason=model.cancel_reason,
        planned_by_name=planner,
        created_at=model.created_at,
    )


class DalTrainingSession:
    def __init__(self, session_factory: sessionmaker[Session] = SessionLocal) -> None:
        self._sessions = session_factory

    def list(self, training_id: uuid.UUID | None = None, request_id: uuid.UUID | None = None) -> list[EntTrainingSession]:
        """Toutes les sessions, par date de début ; la BLL range « à venir d'abord »."""
        with self._sessions() as session:
            query = _select().order_by(TrainingSessionModel.starts_on, TrainingSessionModel.created_at)
            if training_id is not None:
                query = query.where(TrainingSessionModel.training_id == training_id)
            if request_id is not None:
                query = query.where(TrainingSessionModel.request_id == request_id)
            return [_entity(*row) for row in session.execute(query)]

    def get(self, session_id: uuid.UUID) -> EntTrainingSession:
        with self._sessions() as session:
            row = session.execute(_select().where(TrainingSessionModel.id == session_id)).one_or_none()
            if row is None:
                raise RecordNotFoundError("Cette session de formation n'existe pas.")
            return _entity(*row)

    def create(
        self, training_id: uuid.UUID, request_id: uuid.UUID | None, label: str | None, starts_on: date, ends_on: date,
        planned_by: uuid.UUID,
    ) -> EntTrainingSession:
        with self._sessions() as session:
            model = TrainingSessionModel(
                training_id=training_id, request_id=request_id, label=label, starts_on=starts_on, ends_on=ends_on,
                planned_by=planned_by, status=SessionStatus.PLANNED.value,
            )
            session.add(model)
            session.commit()
            session_id = model.id
        return self.get(session_id)

    def update(self, session_id: uuid.UUID, **changes) -> EntTrainingSession:
        """Une modification ordinaire, champ par champ, que le journal voit."""
        with self._sessions() as session:
            model = session.get(TrainingSessionModel, session_id)
            if model is None:
                raise RecordNotFoundError("Cette session de formation n'existe pas.")
            for key, value in changes.items():
                setattr(model, key, value)
            session.commit()
        return self.get(session_id)
