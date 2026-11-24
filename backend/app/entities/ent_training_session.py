from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from uuid import UUID


class SessionStatus(StrEnum):
    """Le statut enregistré d'une session ; « terminée » se déduit des dates."""

    PLANNED = "planned"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class EntTrainingSession:
    """Une session de formation (US-015). Attention à l'homonyme : ce n'est pas
    une session de connexion (`auth_sessions`, GLOSSARY.md)."""

    id: UUID
    training_id: UUID
    training_title: str
    request_id: UUID | None
    request_service: str | None
    label: str | None
    starts_on: date
    ends_on: date
    status: SessionStatus
    cancel_reason: str | None
    planned_by_name: str
    created_at: datetime

    def is_finished(self, today: date) -> bool:
        return self.status is SessionStatus.PLANNED and self.ends_on < today

    def display_status(self, today: date) -> str:
        if self.status is SessionStatus.CANCELLED:
            return "cancelled"
        return "finished" if self.ends_on < today else "planned"
