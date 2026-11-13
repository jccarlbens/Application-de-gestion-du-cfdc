"""Des doubles en mémoire de la DAL et de l'email, pour tester la BLL et les
routes sans base ni serveur d'email."""

import uuid
from dataclasses import replace
from datetime import UTC, datetime

from app.core.exceptions import DuplicateBadgeError, DuplicateEmailError, EmailDeliveryError, UserNotFoundError
from app.entities.ent_user import EntActor, EntNewUser, EntUser, Role, TwoFactorChannel


class FakeEmail:
    def __init__(self, fails: bool = False) -> None:
        self.sent: list[dict] = []
        self._fails = fails

    def send(self, to: str, subject: str, body: str) -> None:
        if self._fails:
            raise EmailDeliveryError("L'email n'a pas pu être envoyé.")
        self.sent.append({"to": to, "subject": subject, "body": body})


class FakeDalUser:
    def __init__(self) -> None:
        self.users: dict[uuid.UUID, EntUser] = {}
        self.tokens: dict[str, dict] = {}
        self.password_hashes: dict[uuid.UUID, str] = {}

    def create_user(self, new_user: EntNewUser, token_hash, token_expires_at, before_commit) -> EntUser:
        if any(u.badge == new_user.badge for u in self.users.values()):
            raise DuplicateBadgeError("Ce numéro de badge est déjà utilisé.")
        if any(u.email == new_user.email for u in self.users.values()):
            raise DuplicateEmailError("Cette adresse email est déjà utilisée.")
        user = EntUser(
            id=uuid.uuid4(),
            badge=new_user.badge,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            email=new_user.email,
            phone=new_user.phone,
            roles=new_user.roles,
            two_factor_channel=TwoFactorChannel.EMAIL,
            is_active=True,
            is_blocked=False,
            has_password=False,
            created_at=datetime.now(UTC),
        )
        before_commit(user)  # s'il échoue, rien n'est enregistré, comme la vraie DAL
        self.users[user.id] = user
        self.tokens[token_hash] = {"user_id": user.id, "expires_at": token_expires_at, "used": False}
        return user

    def get_user(self, user_id):
        if user_id not in self.users:
            raise UserNotFoundError("Ce compte n'existe pas.")
        return self.users[user_id]

    def list_users(self):
        return list(self.users.values())

    def count_active_admins(self) -> int:
        return sum(1 for u in self.users.values() if u.is_active and Role.IT_ADMIN in u.roles)

    def admin_exists(self) -> bool:
        return any(Role.IT_ADMIN in u.roles for u in self.users.values())

    def set_roles(self, user_id, roles):
        self.users[user_id] = replace(self.get_user(user_id), roles=roles)
        return self.users[user_id]

    def set_active(self, user_id, is_active):
        self.users[user_id] = replace(self.get_user(user_id), is_active=is_active)
        return self.users[user_id]

    def use_password_token(self, token_hash, password_hash, now) -> bool:
        token = self.tokens.get(token_hash)
        if token is None or token["used"] or token["expires_at"] <= now:
            return False
        token["used"] = True
        self.password_hashes[token["user_id"]] = password_hash
        user_id = token["user_id"]
        self.users[user_id] = replace(self.users[user_id], has_password=True)
        return True


def actor(*roles: Role) -> EntActor:
    return EntActor(user_id=uuid.uuid4(), roles=frozenset(roles))
