from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.entities.ent_document import EntDocument


class DocumentResponse(BaseModel):
    """Un document de cours, sans son nom sur le disque."""

    id: UUID
    module_id: UUID
    module_title: str
    training_id: UUID
    training_title: str
    file_name: str
    content_type: str
    size_bytes: int
    uploaded_by_name: str
    uploaded_at: datetime
    replaced_by_id: UUID | None

    @classmethod
    def from_entity(cls, document: EntDocument) -> "DocumentResponse":
        return cls(
            id=document.id,
            module_id=document.module_id,
            module_title=document.module_title,
            training_id=document.training_id,
            training_title=document.training_title,
            file_name=document.file_name,
            content_type=document.content_type,
            size_bytes=document.size_bytes,
            uploaded_by_name=document.uploaded_by_name,
            uploaded_at=document.uploaded_at,
            replaced_by_id=document.replaced_by_id,
        )
