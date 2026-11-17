import hashlib
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.bll.bll_password import burn_verification_time, verify_password
from app.core.config import settings
from app.core.exceptions import (
    AccountUnavailableError,
    InvalidCredentialsError,
    NotAuthenticatedError,
    SessionExpiredError,
)
from app.dal.dal_audit import acting_as
from app.dal.dal_auth import DalAuth
from app.dal.dal_user import DalUser
from app.entities.ent_audit import AUTO_BLOCK_LABEL, EntAuditActor
from app.entities.ent_auth import LoginOutcome
from app.entities.ent_user import EntActor, EntUser

# Le seul message pour un numéro de badge inconnu ou un mot de passe faux :
# il ne dit pas lequel des deux est faux (US-004).
WRONG_CREDENTIALS = "Numéro de badge ou mot de passe incorrect."
BLOCKED = "Votre compte est bloqué : contactez l'administrateur informatique."
DEACTIVATED = "Votre compte est désactivé : contactez l'administrateur informatique."
NOT_CONNECTED = "Vous n'êtes pas connecté."
EXPIRED = "Votre session a expiré, reconnectez-vous."


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class LoginResult:
    token: str
    user: EntUser


class BllAuth:
    def __init__(
        self,
        dal_user: DalUser | None = None,
        dal_auth: DalAuth | None = None,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._users = dal_user or DalUser()
        self._auth = dal_auth or DalAuth()
        self._clock = clock

    def login(self, badge: str, password: str) -> LoginResult:
        now = self._clock()
        badge = badge.strip().upper()
        record = self._users.get_login_record(badge)

        if record is None or record.password_hash is None:
            # Même travail qu'avec un vrai compte : le temps de réponse ne
            # révèle pas quels numéros de badge existent.
            burn_verification_time(password)
            outcome = LoginOutcome.UNKNOWN_BADGE if record is None else LoginOutcome.NO_PASSWORD_YET
            self._auth.record_attempt(badge, record.user.id if record else None, outcome, now)
            raise InvalidCredentialsError(WRONG_CREDENTIALS)

        user = record.user
        if not verify_password(record.password_hash, password):
            self._auth.record_attempt(badge, user.id, LoginOutcome.WRONG_PASSWORD, now)
            if user.is_active and not user.is_blocked:
                failures = self._auth.consecutive_failures(user.id, record.failures_counted_since)
                if failures >= settings.max_failed_logins:
                    with acting_as(EntAuditActor(user_id=None, label=AUTO_BLOCK_LABEL)):
                        self._users.block(user.id, now)
            raise InvalidCredentialsError(WRONG_CREDENTIALS)

        # Le mot de passe est bon : on peut dire pourquoi l'accès est refusé.
        if not user.is_active:
            self._auth.record_attempt(badge, user.id, LoginOutcome.DEACTIVATED, now)
            raise AccountUnavailableError(DEACTIVATED)
        if user.is_blocked:
            self._auth.record_attempt(badge, user.id, LoginOutcome.BLOCKED, now)
            raise AccountUnavailableError(BLOCKED)

        token = secrets.token_urlsafe(32)
        self._auth.open_session(user.id, _hash_token(token), now, self._expiry(now))
        self._auth.record_attempt(badge, user.id, LoginOutcome.SUCCESS, now)
        return LoginResult(token=token, user=user)

    def authenticate(self, token: str | None) -> EntActor:
        """L'utilisateur d'un cookie de session ; prolonge la session."""
        if not token:
            raise NotAuthenticatedError(NOT_CONNECTED)
        now = self._clock()
        user_id = self._auth.use_session(_hash_token(token), now, self._expiry(now))
        if user_id is None:
            raise SessionExpiredError(EXPIRED)
        user = self._users.get_user(user_id)
        if not user.is_active or user.is_blocked:
            # Normalement déjà fermée ; par prudence, on la ferme encore.
            self._auth.close_session(_hash_token(token), now)
            raise SessionExpiredError(EXPIRED)
        return EntActor(user_id=user.id, roles=user.roles)

    def current_user(self, actor: EntActor) -> EntUser:
        return self._users.get_user(actor.user_id)

    def logout(self, token: str | None) -> None:
        if token:
            self._auth.close_session(_hash_token(token), self._clock())

    def _expiry(self, now: datetime) -> datetime:
        return now + timedelta(minutes=settings.session_idle_minutes)
