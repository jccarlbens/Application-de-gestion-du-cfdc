from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.entities.ent_training_request import EntTrainingRequest


class TrainingRequestRequest(BaseModel):
    """Des bornes larges : les vraies limites sont vérifiées par la BLL, en français."""

    requesting_service: str = Field(max_length=1000)
    is_external: bool = False
    received_on: date | None = None
    training_id: UUID | None = None
    expected_participants: int | None = None
    desired_period: str | None = Field(default=None, max_length=1000)
    comment: str | None = Field(default=None, max_length=10000)


class DecisionRequest(BaseModel):
    status: str = Field(max_length=20)
    reason: str | None = Field(default=None, max_length=10000)


class TrainingRequestResponse(BaseModel):
    id: UUID
    requesting_service: str
    is_external: bool
    received_on: date
    training_id: UUID
    training_title: str
    expected_participants: int
    desired_period: str | None
    comment: str | None
    status: str
    decided_by_name: str | None
    decided_at: datetime | None
    decision_reason: str | None
    recorded_by_name: str
    created_at: datetime

    @classmethod
    def from_entity(cls, r: EntTrainingRequest) -> "TrainingRequestResponse":
        return cls(**{**r.__dict__, "status": r.status.value})
