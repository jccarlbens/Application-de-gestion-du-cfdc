from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class EntSubdomain:
    """Le second niveau de classement d'une formation (GLOSSARY.md)."""

    id: UUID
    domain_id: UUID
    name: str


@dataclass(frozen=True)
class EntDomain:
    """Le premier niveau de classement, avec ses sous-domaines triés par nom."""

    id: UUID
    name: str
    subdomains: tuple[EntSubdomain, ...]


@dataclass(frozen=True)
class EntTraining:
    """Une formation du catalogue (US-010), avec son classement."""

    id: UUID
    title: str
    description: str | None
    subdomain_id: UUID
    subdomain_name: str
    domain_id: UUID
    domain_name: str
    created_at: datetime


@dataclass(frozen=True)
class EntTrainingInput:
    """Une formation validée par la BLL, prête à enregistrer. `title_key` sert
    à l'unicité : l'intitulé sans majuscules ni espaces en trop."""

    title: str
    title_key: str
    description: str | None
    subdomain_id: UUID


@dataclass(frozen=True)
class EntTrainer:
    """Un formateur, tel que le voit le catalogue : jamais ses données
    personnelles (email, téléphone), seulement son nom et son badge."""

    id: UUID
    first_name: str
    last_name: str
    badge: str
    is_active: bool
    is_trainer: bool


@dataclass(frozen=True)
class EntModule:
    """Un module d'une formation (US-011), avec son formateur s'il est désigné."""

    id: UUID
    training_id: UUID
    title: str
    description: str | None
    trainer: EntTrainer | None
    created_at: datetime


@dataclass(frozen=True)
class EntModuleInput:
    """Un module validé par la BLL, prêt à enregistrer."""

    title: str
    title_key: str
    description: str | None
    trainer_id: UUID | None


@dataclass(frozen=True)
class EntMyModule:
    """Un module tel que le voit son formateur (US-013), avec ses documents en
    vigueur. `documents` contient des `EntDocument` (ent_document)."""

    id: UUID
    title: str
    description: str | None
    documents: tuple


@dataclass(frozen=True)
class EntMyTraining:
    """Une formation où le formateur a au moins un module (US-013)."""

    id: UUID
    title: str
    description: str | None
    domain_name: str
    subdomain_name: str
    modules: tuple[EntMyModule, ...]
