from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.entities.ent_user import EntUser


class LoginOutcome(StrEnum):
    """Le résultat d'une tentative de connexion, tel que noté dans `login_attempts`."""

    SUCCESS = "success"
    UNKNOWN_BADGE = "unknown_badge"
    NO_PASSWORD_YET = "no_password_yet"
    WRONG_PASSWORD = "wrong_password"
    BLOCKED = "blocked"
    DEACTIVATED = "deactivated"


@dataclass(frozen=True)
class EntLoginRecord:
    """Ce que la connexion a besoin de savoir d'un compte, empreinte comprise."""

    user: EntUser
    password_hash: str | None
    failures_counted_since: datetime | None
