from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.v1.dto.dto_training_request import DecisionRequest, TrainingRequestRequest, TrainingRequestResponse
from app.api.v1.security import require_roles
from app.bll.bll_training_request import ADJUSTERS, DECIDERS, READERS, RECORDERS, BllTrainingRequest
from app.entities.ent_user import EntActor

# Les demandes de formation (US-014). Chaque route déclare ses rôles ; la BLL
# vérifie de nouveau et porte les règles fines (décision définitive…).
router = APIRouter(prefix="/training-requests", tags=["training-requests"])


def get_bll_training_request() -> BllTrainingRequest:
    return BllTrainingRequest()


@router.get("", response_model=list[TrainingRequestResponse])
def list_requests(
    status: str | None = None,
    actor: EntActor = Depends(require_roles(*READERS)),
    bll: BllTrainingRequest = Depends(get_bll_training_request),
):
    return [TrainingRequestResponse.from_entity(r) for r in bll.list(actor, status)]


@router.post("", response_model=TrainingRequestResponse, status_code=201)
def create_request(
    body: TrainingRequestRequest,
    actor: EntActor = Depends(require_roles(*RECORDERS)),
    bll: BllTrainingRequest = Depends(get_bll_training_request),
):
    return TrainingRequestResponse.from_entity(bll.create(actor, body.model_dump()))


@router.get("/{request_id}", response_model=TrainingRequestResponse)
def get_request(
    request_id: UUID,
    actor: EntActor = Depends(require_roles(*READERS)),
    bll: BllTrainingRequest = Depends(get_bll_training_request),
):
    return TrainingRequestResponse.from_entity(bll.get(actor, request_id))


@router.put("/{request_id}", response_model=TrainingRequestResponse)
def adjust_request(
    request_id: UUID,
    body: TrainingRequestRequest,
    actor: EntActor = Depends(require_roles(*ADJUSTERS)),
    bll: BllTrainingRequest = Depends(get_bll_training_request),
):
    return TrainingRequestResponse.from_entity(bll.adjust(actor, request_id, body.model_dump()))


@router.post("/{request_id}/decision", response_model=TrainingRequestResponse)
def decide_request(
    request_id: UUID,
    body: DecisionRequest,
    actor: EntActor = Depends(require_roles(*DECIDERS)),
    bll: BllTrainingRequest = Depends(get_bll_training_request),
):
    return TrainingRequestResponse.from_entity(bll.decide(actor, request_id, body.status, body.reason))
