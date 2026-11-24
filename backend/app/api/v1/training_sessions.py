from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.v1.dto.dto_training_session import (
    SessionCancelRequest,
    SessionDatesRequest,
    SessionPlanRequest,
    TrainingSessionResponse,
)
from app.api.v1.security import require_roles
from app.bll.bll_training_session import PLANNERS, READERS, BllTrainingSession
from app.entities.ent_user import EntActor, Role

# Les sessions de formation (US-015). Chaque route déclare ses rôles ; la BLL
# vérifie de nouveau et porte les règles fines (demande validée, session terminée…).
router = APIRouter(tags=["training-sessions"])
READ = require_roles(*READERS)
PLAN = require_roles(*PLANNERS)


def get_bll_training_session() -> BllTrainingSession:
    return BllTrainingSession()


def _out(bll: BllTrainingSession, sessions) -> list[TrainingSessionResponse]:
    today = bll.today()
    return [TrainingSessionResponse.from_entity(s, today) for s in sessions]


@router.get("/training-sessions", response_model=list[TrainingSessionResponse])
def list_sessions(actor: EntActor = Depends(READ), bll: BllTrainingSession = Depends(get_bll_training_session)):
    return _out(bll, bll.list(actor))


@router.get("/trainings/{training_id}/sessions", response_model=list[TrainingSessionResponse])
def training_sessions(training_id: UUID, actor: EntActor = Depends(READ), bll: BllTrainingSession = Depends(get_bll_training_session)):
    return _out(bll, bll.list(actor, training_id=training_id))


@router.get("/training-requests/{request_id}/sessions", response_model=list[TrainingSessionResponse])
def request_sessions(request_id: UUID, actor: EntActor = Depends(READ), bll: BllTrainingSession = Depends(get_bll_training_session)):
    return _out(bll, bll.list(actor, request_id=request_id))


@router.get("/training-sessions/{session_id}", response_model=TrainingSessionResponse)
def get_session(session_id: UUID, actor: EntActor = Depends(READ), bll: BllTrainingSession = Depends(get_bll_training_session)):
    return _out(bll, [bll.get(actor, session_id)])[0]


@router.post("/training-sessions", response_model=TrainingSessionResponse, status_code=201)
def plan_session(body: SessionPlanRequest, actor: EntActor = Depends(PLAN), bll: BllTrainingSession = Depends(get_bll_training_session)):
    session = bll.plan(actor, body.training_id, body.request_id, body.label, body.starts_on, body.ends_on)
    return _out(bll, [session])[0]


@router.put("/training-sessions/{session_id}/dates", response_model=TrainingSessionResponse)
def reschedule_session(
    session_id: UUID, body: SessionDatesRequest, actor: EntActor = Depends(PLAN), bll: BllTrainingSession = Depends(get_bll_training_session)
):
    return _out(bll, [bll.reschedule(actor, session_id, body.starts_on, body.ends_on)])[0]


@router.post("/training-sessions/{session_id}/cancel", response_model=TrainingSessionResponse)
def cancel_session(
    session_id: UUID, body: SessionCancelRequest, actor: EntActor = Depends(PLAN), bll: BllTrainingSession = Depends(get_bll_training_session)
):
    return _out(bll, [bll.cancel(actor, session_id, body.reason)])[0]


@router.post("/training-sessions/{session_id}/restore", response_model=TrainingSessionResponse)
def restore_session(
    session_id: UUID, actor: EntActor = Depends(require_roles(Role.IT_ADMIN)), bll: BllTrainingSession = Depends(get_bll_training_session)
):
    return _out(bll, [bll.restore(actor, session_id)])[0]
