from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

# Les deux auteurs qui ne sont pas un utilisateur connecté (US-003, décision 6).
COMMAND_LINE_LABEL = "Ligne de commande (administrateur)"
PASSWORD_LINK_LABEL = "Titulaire du compte (lien de mot de passe)"
SIGNED_IN_LABEL = "Utilisateur connecté"
AUTO_BLOCK_LABEL = "Blocage automatique (5 échecs)"

# Ce qui remplace la valeur d'un champ secret ou masqué dans le journal.
SECRET_SET = "[secret]"
SECRET_CHANGED = "[secret modifié]"
MASKED = "[masqué]"


class AuditAction(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


@dataclass(frozen=True)
class EntAuditActor:
    """L'auteur d'une modification : un utilisateur, ou un libellé quand
    personne n'est connecté (ligne de commande, lien de mot de passe)."""

    user_id: UUID | None
    label: str


@dataclass(frozen=True)
class EntAuditEntry:
    occurred_at: datetime
    actor_user_id: UUID | None
    actor_label: str
    subject_type: str
    subject_id: str
    table_name: str
    action: AuditAction
    before: dict[str, Any] | None
    after: dict[str, Any] | None
