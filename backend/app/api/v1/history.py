from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.v1.dto.dto_history import HistoryEntryResponse
from app.api.v1.security import get_current_actor
from app.bll.bll_history import BllHistory
from app.entities.ent_user import EntActor

# Le journal se lit et ne s'écrit jamais par l'API (US-003) : cette route est
# la seule, en lecture seule.
router = APIRouter(prefix="/history", tags=["history"])


def get_bll_history() -> BllHistory:
    return BllHistory()


@router.get("/users/{user_id}", response_model=list[HistoryEntryResponse])
def user_history(
    user_id: UUID,
    actor: EntActor = Depends(get_current_actor),
    bll: BllHistory = Depends(get_bll_history),
) -> list[HistoryEntryResponse]:
    return [HistoryEntryResponse.from_entity(e) for e in bll.history(actor, "users", str(user_id))]
