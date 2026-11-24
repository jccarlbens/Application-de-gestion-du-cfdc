from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.entities.ent_training_session import EntTrainingSession


class SessionPlanRequest(BaseModel):
    training_id: UUID | None = None
    request_id: UUID | None = None
    label: str | None = Field(default=None, max_length=1000)
    starts_on: date | None = None
    ends_on: date | None = None


class SessionDatesRequest(BaseModel):
    starts_on: date | None = None
    ends_on: date | None = None


class SessionCancelRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=10000)


class TrainingSessionResponse(BaseModel):
    id: UUID
    training_id: UUID
    training_title: str
    request_id: UUID | None
    request_service: str | None
    label: str | None
    starts_on: date
    ends_on: date
    # « planned », « finished » (déduit des dates) ou « cancelled ».
    status: str
    cancel_reason: str | None
    planned_by_name: str
    created_at: datetime

    @classmethod
    def from_entity(cls, s: EntTrainingSession, today: date) -> "TrainingSessionResponse":
        return cls(**{**s.__dict__, "status": s.display_status(today)})
