from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class Role(StrEnum):
    """Les six rôles du personnel du CFDC (GLOSSARY.md § Acteurs et rôles)."""

    SECRETARY = "secretary"
    COORDINATOR = "coordinator"
    SERVICE_HEAD = "service_head"
    TRAINER = "trainer"
    IT_ADMIN = "it_admin"
    DIRECTION = "direction"


class TwoFactorChannel(StrEnum):
    EMAIL = "email"
    SMS = "sms"


@dataclass(frozen=True)
class EntUser:
    id: UUID
    badge: str
    first_name: str
    last_name: str
    email: str
    phone: str | None
    roles: frozenset[Role]
    two_factor_channel: TwoFactorChannel
    is_active: bool
    is_blocked: bool
    has_password: bool
    created_at: datetime


@dataclass(frozen=True)
class EntNewUser:
    """Ce qu'il faut pour créer un compte, déjà validé par la BLL."""

    badge: str
    first_name: str
    last_name: str
    email: str
    phone: str | None
    roles: frozenset[Role]


@dataclass(frozen=True)
class EntActor:
    """Celui qui agit. `None` à la place d'un acteur : la ligne de commande,
    lancée par l'administrateur sur le serveur, à qui l'on fait confiance."""

    user_id: UUID
    roles: frozenset[Role]
