from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.v1.dto.dto_training import (
    DomainResponse,
    ModuleRequest,
    ModuleResponse,
    NameRequest,
    SubdomainResponse,
    TrainerAssignRequest,
    TrainerResponse,
    TrainingRequest,
    TrainingResponse,
)
from app.api.v1.security import require_roles
from app.bll.bll_training import CATALOGUE_READERS, TRAINING_WRITERS, BllTraining
from app.entities.ent_user import EntActor, Role

# Le catalogue (US-010). Chaque route déclare ses rôles ; la BLL vérifie de
# nouveau et porte les règles fines.
READERS = require_roles(*CATALOGUE_READERS)
WRITERS = require_roles(*TRAINING_WRITERS)
ADMIN_ONLY = require_roles(Role.IT_ADMIN)

router = APIRouter(tags=["trainings"])


def get_bll_training() -> BllTraining:
    return BllTraining()


# --- Domaines et sous-domaines -------------------------------------------------


@router.get("/domains", response_model=list[DomainResponse])
def list_domains(actor: EntActor = Depends(READERS), bll: BllTraining = Depends(get_bll_training)):
    return [DomainResponse.from_entity(d) for d in bll.list_domains(actor)]


@router.post("/domains", response_model=DomainResponse, status_code=201)
def add_domain(body: NameRequest, actor: EntActor = Depends(ADMIN_ONLY), bll: BllTraining = Depends(get_bll_training)):
    return DomainResponse.from_entity(bll.add_domain(actor, body.name))


@router.put("/domains/{domain_id}", response_model=DomainResponse)
def rename_domain(
    domain_id: UUID, body: NameRequest, actor: EntActor = Depends(ADMIN_ONLY), bll: BllTraining = Depends(get_bll_training)
):
    return DomainResponse.from_entity(bll.rename_domain(actor, domain_id, body.name))


@router.post("/domains/{domain_id}/subdomains", response_model=SubdomainResponse, status_code=201)
def add_subdomain(
    domain_id: UUID, body: NameRequest, actor: EntActor = Depends(ADMIN_ONLY), bll: BllTraining = Depends(get_bll_training)
):
    return SubdomainResponse.from_entity(bll.add_subdomain(actor, domain_id, body.name))


@router.put("/subdomains/{subdomain_id}", response_model=SubdomainResponse)
def rename_subdomain(
    subdomain_id: UUID,
    body: NameRequest,
    actor: EntActor = Depends(ADMIN_ONLY),
    bll: BllTraining = Depends(get_bll_training),
):
    return SubdomainResponse.from_entity(bll.rename_subdomain(actor, subdomain_id, body.name))


# --- Formations -------------------------------------------------------------------


@router.get("/trainings", response_model=list[TrainingResponse])
def list_trainings(actor: EntActor = Depends(READERS), bll: BllTraining = Depends(get_bll_training)):
    return [TrainingResponse.from_entity(t) for t in bll.list_trainings(actor)]


@router.post("/trainings", response_model=TrainingResponse, status_code=201)
def create_training(
    body: TrainingRequest, actor: EntActor = Depends(WRITERS), bll: BllTraining = Depends(get_bll_training)
):
    return TrainingResponse.from_entity(bll.create_training(actor, body.title, body.description, body.subdomain_id))


@router.get("/trainings/{training_id}", response_model=TrainingResponse)
def get_training(training_id: UUID, actor: EntActor = Depends(READERS), bll: BllTraining = Depends(get_bll_training)):
    return TrainingResponse.from_entity(bll.get_training(actor, training_id))


@router.put("/trainings/{training_id}", response_model=TrainingResponse)
def update_training(
    training_id: UUID,
    body: TrainingRequest,
    actor: EntActor = Depends(ADMIN_ONLY),
    bll: BllTraining = Depends(get_bll_training),
):
    return TrainingResponse.from_entity(
        bll.update_training(actor, training_id, body.title, body.description, body.subdomain_id)
    )


# --- Modules et formateurs (US-011) ---------------------------------------------


@router.get("/trainers", response_model=list[TrainerResponse])
def list_trainers(actor: EntActor = Depends(WRITERS), bll: BllTraining = Depends(get_bll_training)):
    return [TrainerResponse.from_entity(t) for t in bll.list_trainers(actor)]


@router.get("/trainings/{training_id}/modules", response_model=list[ModuleResponse])
def list_modules(training_id: UUID, actor: EntActor = Depends(READERS), bll: BllTraining = Depends(get_bll_training)):
    return [ModuleResponse.from_entity(m) for m in bll.list_modules(actor, training_id)]


@router.post("/trainings/{training_id}/modules", response_model=ModuleResponse, status_code=201)
def add_module(
    training_id: UUID, body: ModuleRequest, actor: EntActor = Depends(WRITERS), bll: BllTraining = Depends(get_bll_training)
):
    return ModuleResponse.from_entity(bll.add_module(actor, training_id, body.title, body.description, body.trainer_id))


@router.post("/modules/{module_id}/trainer", response_model=ModuleResponse)
def assign_trainer(
    module_id: UUID,
    body: TrainerAssignRequest,
    actor: EntActor = Depends(WRITERS),
    bll: BllTraining = Depends(get_bll_training),
):
    """Ceux qui enregistrent désignent le formateur d'un module « à désigner » ;
    changer un formateur déjà désigné est vérifié par la BLL (administrateur)."""
    return ModuleResponse.from_entity(bll.assign_trainer(actor, module_id, body.trainer_id))


@router.put("/modules/{module_id}", response_model=ModuleResponse)
def update_module(
    module_id: UUID, body: ModuleRequest, actor: EntActor = Depends(ADMIN_ONLY), bll: BllTraining = Depends(get_bll_training)
):
    return ModuleResponse.from_entity(
        bll.update_module(actor, module_id, body.title, body.description, body.trainer_id)
    )
