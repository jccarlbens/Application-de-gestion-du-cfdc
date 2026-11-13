import uuid
from collections.abc import Callable
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship, sessionmaker

from app.core.exceptions import DuplicateBadgeError, DuplicateEmailError, UserNotFoundError
from app.dal.database import Base, SessionLocal
from app.entities.ent_user import EntNewUser, EntUser, Role, TwoFactorChannel


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    badge: Mapped[str] = mapped_column(String(6), unique=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    phone: Mapped[str | None] = mapped_column(String(30))
    two_factor_channel: Mapped[str] = mapped_column(String(10), default=TwoFactorChannel.EMAIL.value)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    roles: Mapped[list["UserRoleModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )


class UserRoleModel(Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(String(20))

    user: Mapped[UserModel] = relationship(back_populates="roles")


class PasswordTokenModel(Base):
    """Un lien pour choisir son mot de passe. Seule l'empreinte du jeton est
    gardée : une fuite de la base ne donne aucun lien utilisable."""

    __tablename__ = "password_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


def _to_entity(model: UserModel) -> EntUser:
    return EntUser(
        id=model.id,
        badge=model.badge,
        first_name=model.first_name,
        last_name=model.last_name,
        email=model.email,
        phone=model.phone,
        roles=frozenset(Role(r.role) for r in model.roles),
        two_factor_channel=TwoFactorChannel(model.two_factor_channel),
        is_active=model.is_active,
        is_blocked=model.is_blocked,
        has_password=model.password_hash is not None,
        created_at=model.created_at,
    )


def _translate_integrity_error(error: IntegrityError) -> Exception:
    message = str(error.orig)
    if "badge" in message:
        return DuplicateBadgeError("Ce numéro de badge est déjà utilisé.")
    if "email" in message:
        return DuplicateEmailError("Cette adresse email est déjà utilisée.")
    return error


class DalUser:
    def __init__(self, session_factory: sessionmaker[Session] = SessionLocal) -> None:
        self._sessions = session_factory

    def create_user(
        self,
        new_user: EntNewUser,
        token_hash: str,
        token_expires_at: datetime,
        before_commit: Callable[[EntUser], None],
    ) -> EntUser:
        """Crée le compte et son lien de mot de passe dans une seule transaction.
        `before_commit` envoie l'email : s'il échoue, rien n'est enregistré."""
        with self._sessions() as session:
            model = UserModel(
                badge=new_user.badge,
                first_name=new_user.first_name,
                last_name=new_user.last_name,
                email=new_user.email,
                phone=new_user.phone,
                roles=[UserRoleModel(role=role.value) for role in sorted(new_user.roles)],
            )
            session.add(model)
            try:
                session.flush()
            except IntegrityError as error:
                session.rollback()
                raise _translate_integrity_error(error) from error
            session.add(
                PasswordTokenModel(user_id=model.id, token_hash=token_hash, expires_at=token_expires_at)
            )
            session.flush()
            session.refresh(model)
            user = _to_entity(model)
            before_commit(user)
            session.commit()
            return user

    def get_user(self, user_id: uuid.UUID) -> EntUser:
        with self._sessions() as session:
            model = session.get(UserModel, user_id)
            if model is None:
                raise UserNotFoundError("Ce compte n'existe pas.")
            return _to_entity(model)

    def list_users(self) -> list[EntUser]:
        with self._sessions() as session:
            models = session.scalars(select(UserModel).order_by(UserModel.last_name, UserModel.first_name))
            return [_to_entity(m) for m in models]

    def count_active_admins(self) -> int:
        with self._sessions() as session:
            return session.scalar(
                select(func.count(UserModel.id.distinct()))
                .join(UserRoleModel)
                .where(UserRoleModel.role == Role.IT_ADMIN.value, UserModel.is_active.is_(True))
            ) or 0

    def admin_exists(self) -> bool:
        with self._sessions() as session:
            return (
                session.scalar(
                    select(func.count()).select_from(UserRoleModel).where(UserRoleModel.role == Role.IT_ADMIN.value)
                )
                or 0
            ) > 0

    def set_roles(self, user_id: uuid.UUID, roles: frozenset[Role]) -> EntUser:
        with self._sessions() as session:
            model = session.get(UserModel, user_id)
            if model is None:
                raise UserNotFoundError("Ce compte n'existe pas.")
            model.roles = [UserRoleModel(role=role.value) for role in sorted(roles)]
            session.commit()
            session.refresh(model)
            return _to_entity(model)

    def set_active(self, user_id: uuid.UUID, is_active: bool) -> EntUser:
        with self._sessions() as session:
            model = session.get(UserModel, user_id)
            if model is None:
                raise UserNotFoundError("Ce compte n'existe pas.")
            model.is_active = is_active
            session.commit()
            session.refresh(model)
            return _to_entity(model)

    def use_password_token(self, token_hash: str, password_hash: str, now: datetime) -> bool:
        """Enregistre le mot de passe si le lien est valable, et le consomme.
        Renvoie False si le lien est inconnu, expiré ou déjà utilisé."""
        with self._sessions() as session:
            used = session.execute(
                update(PasswordTokenModel)
                .where(
                    PasswordTokenModel.token_hash == token_hash,
                    PasswordTokenModel.used_at.is_(None),
                    PasswordTokenModel.expires_at > now,
                )
                .values(used_at=now)
                .returning(PasswordTokenModel.user_id)
            ).scalar_one_or_none()
            if used is None:
                session.rollback()
                return False
            session.execute(update(UserModel).where(UserModel.id == used).values(password_hash=password_hash))
            session.commit()
            return True

