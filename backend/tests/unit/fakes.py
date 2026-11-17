"""Des doubles en mémoire de la DAL et de l'email, pour tester la BLL et les
routes sans base ni serveur d'email."""

import uuid
from dataclasses import replace
from datetime import UTC, datetime

from app.core.exceptions import DuplicateBadgeError, DuplicateEmailError, EmailDeliveryError, UserNotFoundError
from app.entities.ent_auth import EntLoginRecord, LoginOutcome
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
        self.failures_since: dict[uuid.UUID, datetime] = {}
        self.auth: "FakeDalAuth | None" = None  # pour fermer les sessions, comme la vraie DAL

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

    def set_active(self, user_id, is_active, now=None):
        self.users[user_id] = replace(self.get_user(user_id), is_active=is_active)
        if not is_active and self.auth:
            self.auth.close_user_sessions(user_id)
        return self.users[user_id]

    def get_login_record(self, badge):
        user = next((u for u in self.users.values() if u.badge == badge), None)
        if user is None:
            return None
        return EntLoginRecord(user, self.password_hashes.get(user.id), self.failures_since.get(user.id))

    def get_user_by_badge(self, badge):
        user = next((u for u in self.users.values() if u.badge == badge), None)
        if user is None:
            raise UserNotFoundError("Aucun compte n'a ce numéro de badge.")
        return user

    def block(self, user_id, now) -> None:
        self.users[user_id] = replace(self.users[user_id], is_blocked=True)
        if self.auth:
            self.auth.close_user_sessions(user_id)

    def unblock(self, user_id, now):
        self.users[user_id] = replace(self.get_user(user_id), is_blocked=False)
        self.failures_since[user_id] = now
        return self.users[user_id]

    def add_user_with_password(self, badge: str, password_hash: str, roles=(Role.SECRETARY,)) -> EntUser:
        user = EntUser(
            id=uuid.uuid4(), badge=badge, first_name="Marie", last_name="Joseph", email=f"{badge}@example.test",
            phone=None, roles=frozenset(roles), two_factor_channel=TwoFactorChannel.EMAIL, is_active=True,
            is_blocked=False, has_password=True, created_at=datetime.now(UTC),
        )
        self.users[user.id] = user
        self.password_hashes[user.id] = password_hash
        return user


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


class FakeDalAuth:
    def __init__(self) -> None:
        self.attempts: list[dict] = []
        self.sessions: dict[str, dict] = {}

    def record_attempt(self, badge_entered, user_id, outcome: LoginOutcome, now) -> None:
        self.attempts.append({"badge": badge_entered, "user_id": user_id, "outcome": outcome, "at": now})

    def consecutive_failures(self, user_id, counted_since) -> int:
        count = 0
        for attempt in reversed(self.attempts):
            if attempt["user_id"] != user_id:
                continue
            if attempt["outcome"] is LoginOutcome.SUCCESS or (counted_since and attempt["at"] <= counted_since):
                break
            count += 1
        return count

    def open_session(self, user_id, token_hash, now, expires_at) -> None:
        self.sessions[token_hash] = {"user_id": user_id, "expires_at": expires_at, "closed": False}

    def use_session(self, token_hash, now, new_expiry):
        session = self.sessions.get(token_hash)
        if session is None or session["closed"] or session["expires_at"] <= now:
            return None
        session["expires_at"] = new_expiry
        return session["user_id"]

    def close_session(self, token_hash, now) -> None:
        if token_hash in self.sessions:
            self.sessions[token_hash]["closed"] = True

    def close_user_sessions(self, user_id) -> None:
        for session in self.sessions.values():
            if session["user_id"] == user_id:
                session["closed"] = True
