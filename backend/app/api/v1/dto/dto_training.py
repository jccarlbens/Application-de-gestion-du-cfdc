from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.entities.ent_training import EntDomain, EntModule, EntMyTraining, EntSubdomain, EntTrainer, EntTraining

# Des bornes larges, seulement contre les envois démesurés : les vraies
# limites (200 et 2 000 caractères) sont vérifiées par la BLL, avec un message
# en français.


class TrainingRequest(BaseModel):
    title: str = Field(max_length=1000)
    description: str | None = Field(default=None, max_length=10000)
    subdomain_id: UUID


class NameRequest(BaseModel):
    name: str = Field(max_length=1000)


class SubdomainResponse(BaseModel):
    id: UUID
    domain_id: UUID
    name: str

    @classmethod
    def from_entity(cls, subdomain: EntSubdomain) -> "SubdomainResponse":
        return cls(id=subdomain.id, domain_id=subdomain.domain_id, name=subdomain.name)


class DomainResponse(BaseModel):
    id: UUID
    name: str
    subdomains: list[SubdomainResponse]

    @classmethod
    def from_entity(cls, domain: EntDomain) -> "DomainResponse":
        return cls(
            id=domain.id,
            name=domain.name,
            subdomains=[SubdomainResponse.from_entity(s) for s in domain.subdomains],
        )


class TrainingResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    subdomain_id: UUID
    subdomain_name: str
    domain_id: UUID
    domain_name: str
    created_at: datetime

    @classmethod
    def from_entity(cls, training: EntTraining) -> "TrainingResponse":
        return cls(**training.__dict__)


class ModuleRequest(BaseModel):
    title: str = Field(max_length=1000)
    description: str | None = Field(default=None, max_length=10000)
    trainer_id: UUID | None = None


class TrainerAssignRequest(BaseModel):
    trainer_id: UUID


class TrainerResponse(BaseModel):
    """Le formateur, sans ses données personnelles (email, téléphone)."""

    id: UUID
    first_name: str
    last_name: str
    badge: str
    is_active: bool
    is_trainer: bool

    @classmethod
    def from_entity(cls, trainer: EntTrainer) -> "TrainerResponse":
        return cls(**trainer.__dict__)


class ModuleResponse(BaseModel):
    id: UUID
    training_id: UUID
    title: str
    description: str | None
    trainer: TrainerResponse | None
    created_at: datetime

    @classmethod
    def from_entity(cls, module: EntModule) -> "ModuleResponse":
        return cls(
            id=module.id,
            training_id=module.training_id,
            title=module.title,
            description=module.description,
            trainer=TrainerResponse.from_entity(module.trainer) if module.trainer else None,
            created_at=module.created_at,
        )


class MyDocumentResponse(BaseModel):
    """Un document vu par son formateur : sans « déposé par » (US-013, décision 3)."""

    id: UUID
    file_name: str
    size_bytes: int
    uploaded_at: datetime


class MyModuleResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    documents: list[MyDocumentResponse]


class MyTrainingResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    domain_name: str
    subdomain_name: str
    modules: list[MyModuleResponse]

    @classmethod
    def from_entity(cls, training: EntMyTraining) -> "MyTrainingResponse":
        return cls(
            id=training.id,
            title=training.title,
            description=training.description,
            domain_name=training.domain_name,
            subdomain_name=training.subdomain_name,
            modules=[
                MyModuleResponse(
                    id=m.id,
                    title=m.title,
                    description=m.description,
                    documents=[
                        MyDocumentResponse(id=d.id, file_name=d.file_name, size_bytes=d.size_bytes, uploaded_at=d.uploaded_at)
                        for d in m.documents
                    ],
                )
                for m in training.modules
            ],
        )
