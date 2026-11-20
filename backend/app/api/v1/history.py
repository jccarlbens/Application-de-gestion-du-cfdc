from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.v1.dto.dto_history import HistoryEntryResponse
from app.api.v1.security import require_roles
from app.bll.bll_history import ANY_READER, BllHistory
from app.entities.ent_user import EntActor

# Le journal se lit et ne s'écrit jamais par l'API (US-003) : cette route est
# la seule, en lecture seule.
router = APIRouter(prefix="/history", tags=["history"])


def get_bll_history() -> BllHistory:
    return BllHistory()


@router.get("/{subject_type}/{subject_id}", response_model=list[HistoryEntryResponse])
def history(
    subject_type: str,
    subject_id: UUID,
    actor: EntActor = Depends(require_roles(*ANY_READER)),
    bll: BllHistory = Depends(get_bll_history),
) -> list[HistoryEntryResponse]:
    """L'historique d'une fiche : `users`, `trainings`, `domains` ou
    `subdomains`. Qui lit quel genre de fiche : `bll_history._READERS`."""
    return [HistoryEntryResponse.from_entity(e) for e in bll.history(actor, subject_type, str(subject_id))]
