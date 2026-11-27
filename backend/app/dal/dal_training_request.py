"""Les demandes de formation (US-014), journalisées. Le nom `training_requests`
évite l'homonyme avec les demandes de correction (Epic 5)."""

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, func, select
from sqlalchemy.orm import Mapped, Session, aliased, mapped_column, sessionmaker

from app.core.exceptions import RecordNotFoundError
from app.dal.dal_audit import AuditPolicy
from app.dal.dal_training import TrainingModel
from app.dal.dal_user import UserModel
from app.dal.database import Base, SessionLocal
from app.entities.ent_training_request import EntTrainingRequest, EntTrainingRequestInput, RequestStatus


class TrainingRequestModel(Base):
    __tablename__ = "training_requests"
    __audit__ = AuditPolicy(subject=lambda r: ("training_requests", r.id))

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    requesting_service: Mapped[str] = mapped_column(String(150))
    is_external: Mapped[bool] = mapped_column(Boolean, default=False)
    # Une date du calendrier de l'AAN, sans heure ni fuseau (E3-8).
    received_on: Mapped[date] = mapped_column(Date, index=True)
    training_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trainings.id"), index=True)
    expected_participants: Mapped[int] = mapped_column(Integer)
    desired_period: Mapped[str | None] = mapped_column(String(100))
    comment: Mapped[str | None] = mapped_column(String(2000))
    status: Mapped[str] = mapped_column(String(10), default=RequestStatus.PENDING.value, index=True)
    decided_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decision_reason: Mapped[str | None] = mapped_column(String(2000))
    recorded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.clock_timestamp())


_DECIDER = aliased(UserModel)
_RECORDER = aliased(UserModel)


def _name(user):
    return (user.first_name + " " + user.last_name + " (" + user.badge + ")")


def _select():
    return (
        select(
            TrainingRequestModel,
            TrainingModel.title,
            _name(_DECIDER).label("decider"),
            _name(_RECORDER).label("recorder"),
        )
        .join(TrainingModel, TrainingModel.id == TrainingRequestModel.training_id)
        .join(_RECORDER, _RECORDER.id == TrainingRequestModel.recorded_by)
        .outerjoin(_DECIDER, _DECIDER.id == TrainingRequestModel.decided_by)
    )


def _entity(model: TrainingRequestModel, training_title: str, decider: str | None, recorder: str) -> EntTrainingRequest:
    return EntTrainingRequest(
        id=model.id,
        requesting_service=model.requesting_service,
        is_external=model.is_external,
        received_on=model.received_on,
        training_id=model.training_id,
        training_title=training_title,
        expected_participants=model.expected_participants,
        desired_period=model.desired_period,
        comment=model.comment,
        status=RequestStatus(model.status),
        decided_by_name=decider,
        decided_at=model.decided_at,
        decision_reason=model.decision_reason,
        recorded_by_name=recorder,
        created_at=model.created_at,
    )


class DalTrainingRequest:
    def __init__(self, session_factory: sessionmaker[Session] = SessionLocal) -> None:
        self._sessions = session_factory

    def list(self, status: RequestStatus | None = None) -> list[EntTrainingRequest]:
        """De la plus récente à la plus ancienne (US-014, décision 5)."""
        with self._sessions() as session:
            query = _select().order_by(TrainingRequestModel.received_on.desc(), TrainingRequestModel.created_at.desc())
            if status is not None:
                query = query.where(TrainingRequestModel.status == status.value)
            return [_entity(*row) for row in session.execute(query)]

    def get(self, request_id: uuid.UUID) -> EntTrainingRequest:
        with self._sessions() as session:
            row = session.execute(_select().where(TrainingRequestModel.id == request_id)).one_or_none()
            if row is None:
                raise RecordNotFoundError("Cette demande de formation n'existe pas.")
            return _entity(*row)

    def create(self, data: EntTrainingRequestInput, recorded_by: uuid.UUID) -> EntTrainingRequest:
        with self._sessions() as session:
            model = TrainingRequestModel(**data.__dict__, recorded_by=recorded_by, status=RequestStatus.PENDING.value)
            session.add(model)
            session.commit()
            request_id = model.id
        return self.get(request_id)

    def update(self, request_id: uuid.UUID, data: EntTrainingRequestInput) -> EntTrainingRequest:
        """Une modification ordinaire, champ par champ, que le journal voit."""
        with self._sessions() as session:
            model = self._model(session, request_id)
            for key, value in data.__dict__.items():
                setattr(model, key, value)
            session.commit()
        return self.get(request_id)

    def decide(
        self, request_id: uuid.UUID, status: RequestStatus, decided_by: uuid.UUID, reason: str | None, now: datetime
    ) -> EntTrainingRequest:
        with self._sessions() as session:
            model = self._model(session, request_id)
            model.status = status.value
            model.decided_by = decided_by
            model.decided_at = now
            model.decision_reason = reason
            session.commit()
        return self.get(request_id)

    @staticmethod
    def _model(session: Session, request_id: uuid.UUID) -> TrainingRequestModel:
        model = session.get(TrainingRequestModel, request_id)
        if model is None:
            raise RecordNotFoundError("Cette demande de formation n'existe pas.")
        return model
