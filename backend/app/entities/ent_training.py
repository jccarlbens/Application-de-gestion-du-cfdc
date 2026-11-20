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
