from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.entities.ent_training import EntDomain, EntSubdomain, EntTraining

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
