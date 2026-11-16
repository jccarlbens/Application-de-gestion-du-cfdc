from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.entities.ent_audit import EntAuditEntry


class HistoryEntryResponse(BaseModel):
    occurred_at: datetime
    actor_user_id: UUID | None
    actor_label: str
    table_name: str
    action: str
    before: dict[str, Any] | None
    after: dict[str, Any] | None

    @classmethod
    def from_entity(cls, entry: EntAuditEntry) -> "HistoryEntryResponse":
        return cls(
            occurred_at=entry.occurred_at,
            actor_user_id=entry.actor_user_id,
            actor_label=entry.actor_label,
            table_name=entry.table_name,
            action=entry.action.value,
            before=entry.before,
            after=entry.after,
        )
