from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class EntDocument:
    """Un document de cours (US-012), avec ce qu'il faut pour l'afficher et
    décider qui l'ouvre : sa formation, son module et le formateur actuel."""

    id: UUID
    module_id: UUID
    module_title: str
    training_id: UUID
    training_title: str
    trainer_id: UUID | None
    file_name: str
    content_type: str
    size_bytes: int
    uploaded_by_name: str
    uploaded_at: datetime
    replaced_by_id: UUID | None
    storage_name: str

    @property
    def is_current(self) -> bool:
        return self.replaced_by_id is None


@dataclass(frozen=True)
class EntNewDocument:
    """Un fichier vérifié par la BLL, prêt à ranger."""

    file_name: str
    content_type: str
    content: bytes
