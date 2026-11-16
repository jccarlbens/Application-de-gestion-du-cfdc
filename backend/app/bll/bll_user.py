import hashlib
import re
import secrets
from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.bll.bll_password import check_strength, hash_password
from app.core.config import settings
from app.core.exceptions import (
    AdminAlreadyExistsError,
    ForbiddenError,
    InvalidInputError,
    InvalidPasswordLinkError,
    LastAdminError,
)
from app.dal.dal_email import DalEmail
from app.dal.dal_user import DalUser
from app.entities.ent_user import EntActor, EntNewUser, EntUser, Role

# Une lettre majuscule, deux chiffres, un tiret, deux chiffres (US-002, décision 2B).
BADGE_PATTERN = re.compile(r"^[A-Z]\d{2}-\d{2}$")
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Qui peut créer un compte, et avec quels rôles (PRD.md §5 ; US-002, décision 4A).
_GRANTABLE_ROLES = {
    Role.IT_ADMIN: frozenset(Role),
    Role.COORDINATOR: frozenset(Role) - {Role.IT_ADMIN},
}


@dataclass(frozen=True)
class AccountInput:
    """Ce que saisit celui qui crée le compte, avant validation."""

    badge: str
    first_name: str
    last_name: str
    email: str
    phone: str | None
    roles: Iterable[str]


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class BllUser:
    def __init__(
        self,
        dal: DalUser | None = None,
        email: DalEmail | None = None,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._dal = dal or DalUser()
        self._email = email or DalEmail()
        self._clock = clock

    # --- Création ---------------------------------------------------------

    def create_first_admin(self, account: AccountInput) -> EntUser:
        """La commande `create-admin`, lancée une fois sur le serveur."""
        if self._dal.admin_exists():
            raise AdminAlreadyExistsError("Un administrateur existe déjà : utilisez create-user.")
        with_admin_role = replace(account, roles=[*account.roles, Role.IT_ADMIN.value])
        return self._save_and_send_link(self._validate(with_admin_role))

    def create_user(self, actor: EntActor | None, account: AccountInput) -> EntUser:
        """`actor` à None : la commande `create-user`, à qui l'on fait confiance."""
        new_user = self._validate(account)
        if actor is not None:
            grantable = frozenset().union(*(_GRANTABLE_ROLES.get(role, frozenset()) for role in actor.roles))
            if not grantable:
                raise ForbiddenError("Seuls l'administrateur informatique et le coordonnateur créent des comptes.")
            if not new_user.roles <= grantable:
                raise ForbiddenError("Seul l'administrateur informatique peut donner le rôle d'administrateur.")
        return self._save_and_send_link(new_user)

    def _validate(self, account: AccountInput) -> EntNewUser:
        badge = account.badge.strip().upper()
        if not BADGE_PATTERN.match(badge):
            raise InvalidInputError("Le badge doit avoir la forme A00-00 : une lettre, deux chiffres, un tiret, deux chiffres.")
        first_name, last_name = account.first_name.strip(), account.last_name.strip()
        if not first_name or not last_name:
            raise InvalidInputError("Le nom et le prénom sont obligatoires.")
        email = account.email.strip().lower()
        if not _EMAIL_PATTERN.match(email):
            raise InvalidInputError("L'adresse email n'est pas valide.")
        phone = (account.phone or "").strip() or None
        try:
            roles = frozenset(Role(r) for r in account.roles)
        except ValueError as error:
            raise InvalidInputError("Un des rôles n'existe pas.") from error
        if not roles:
            raise InvalidInputError("Un compte a au moins un rôle.")
        return EntNewUser(badge, first_name, last_name, email, phone, roles)

    def _save_and_send_link(self, new_user: EntNewUser) -> EntUser:
        token = secrets.token_urlsafe(32)
        expires_at = self._clock() + timedelta(hours=settings.password_link_hours)

        def send_link(user: EntUser) -> None:
            link = f"{settings.app_base_url}/mot-de-passe?jeton={token}"
            self._email.send(
                to=user.email,
                subject="CFDC — Choisissez votre mot de passe",
                body=(
                    f"Bonjour {user.first_name},\n\n"
                    "Un compte a été créé pour vous dans l'application de gestion des formations du CFDC.\n"
                    f"Votre numéro de badge : {user.badge}\n\n"
                    f"Choisissez votre mot de passe en ouvrant ce lien, valable {settings.password_link_hours} heures :\n"
                    f"{link}\n\n"
                    "Si vous n'attendiez pas ce message, ignorez-le.\n"
                ),
            )

        return self._dal.create_user(new_user, _hash_token(token), expires_at, before_commit=send_link)

    # --- Gestion par l'administrateur ----------------------------------------

    def list_users(self, actor: EntActor) -> list[EntUser]:
        if not actor.roles & {Role.IT_ADMIN, Role.COORDINATOR}:
            raise ForbiddenError("Seuls l'administrateur informatique et le coordonnateur voient les comptes.")
        return self._dal.list_users()

    def set_roles(self, actor: EntActor, user_id: UUID, roles: Iterable[str]) -> EntUser:
        self._require_admin(actor)
        try:
            new_roles = frozenset(Role(r) for r in roles)
        except ValueError as error:
            raise InvalidInputError("Un des rôles n'existe pas.") from error
        if not new_roles:
            raise InvalidInputError("Un compte a au moins un rôle.")
        user = self._dal.get_user(user_id)
        if Role.IT_ADMIN in user.roles and Role.IT_ADMIN not in new_roles and user.is_active:
            self._refuse_if_last_admin()
        return self._dal.set_roles(user_id, new_roles)

    def set_active(self, actor: EntActor, user_id: UUID, is_active: bool) -> EntUser:
        self._require_admin(actor)
        user = self._dal.get_user(user_id)
        if not is_active and user.is_active and Role.IT_ADMIN in user.roles:
            self._refuse_if_last_admin()
        return self._dal.set_active(user_id, is_active)

    def _require_admin(self, actor: EntActor) -> None:
        if Role.IT_ADMIN not in actor.roles:
            raise ForbiddenError("Seul l'administrateur informatique peut faire cela.")

    def _refuse_if_last_admin(self) -> None:
        if self._dal.count_active_admins() <= 1:
            raise LastAdminError("C'est le dernier administrateur actif : l'application ne peut pas rester sans administrateur.")

    # --- Mot de passe par le lien ----------------------------------------------

    def set_password_with_link(self, token: str, password: str) -> None:
        check_strength(password)
        if not self._dal.use_password_token(_hash_token(token), hash_password(password), self._clock()):
            raise InvalidPasswordLinkError(
                "Ce lien n'est plus valable : il a expiré ou a déjà servi."
            )
