from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from uuid import UUID


class RequestStatus(StrEnum):
    """Le statut d'une demande de formation (affinage de l'Epic 3, Q2)."""

    PENDING = "pending"
    APPROVED = "approved"
    REFUSED = "refused"


@dataclass(frozen=True)
class EntTrainingRequestInput:
    """Ce qui se saisit et s'ajuste d'une demande, validé par la BLL."""

    requesting_service: str
    is_external: bool
    received_on: date
    training_id: UUID
    expected_participants: int
    desired_period: str | None
    comment: str | None


@dataclass(frozen=True)
class EntTrainingRequest:
    """Une demande de formation (US-014). Attention à l'homonyme : ce n'est pas
    une demande de correction (GLOSSARY.md)."""

    id: UUID
    requesting_service: str
    is_external: bool
    received_on: date
    training_id: UUID
    training_title: str
    expected_participants: int
    desired_period: str | None
    comment: str | None
    status: RequestStatus
    decided_by_name: str | None
    decided_at: datetime | None
    decision_reason: str | None
    recorded_by_name: str
    created_at: datetime
