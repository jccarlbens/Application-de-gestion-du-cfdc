import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, func, select, update
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from app.dal.database import Base, SessionLocal
from app.entities.ent_auth import LoginOutcome


class LoginAttemptModel(Base):
    """Chaque tentative de connexion, réussie ou non, sans le mot de passe
    (US-004). Les échecs consécutifs se comptent ici, pas dans `users`."""

    __tablename__ = "login_attempts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    badge_entered: Mapped[str] = mapped_column(String(20))
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    success: Mapped[bool] = mapped_column(Boolean)
    outcome: Mapped[str] = mapped_column(String(20))


class AuthSessionModel(Base):
    """Une session de connexion (à ne pas confondre avec une session de
    formation). Seule l'empreinte du jeton du cookie est gardée."""

    __tablename__ = "auth_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


def close_user_sessions(session: Session, user_id: uuid.UUID, now: datetime) -> None:
    """Ferme toutes les sessions ouvertes d'un compte, dans la transaction de
    l'appelant (désactivation ou blocage) : l'effet est immédiat."""
    session.execute(
        update(AuthSessionModel)
        .where(AuthSessionModel.user_id == user_id, AuthSessionModel.closed_at.is_(None))
        .values(closed_at=now)
    )


class DalAuth:
    def __init__(self, session_factory: sessionmaker[Session] = SessionLocal) -> None:
        self._sessions = session_factory

    # --- Tentatives -----------------------------------------------------------

    def record_attempt(
        self, badge_entered: str, user_id: uuid.UUID | None, outcome: LoginOutcome, now: datetime
    ) -> None:
        with self._sessions() as session:
            session.add(
                LoginAttemptModel(
                    occurred_at=now,
                    badge_entered=badge_entered[:20],
                    user_id=user_id,
                    success=outcome is LoginOutcome.SUCCESS,
                    outcome=outcome.value,
                )
            )
            session.commit()

    def consecutive_failures(self, user_id: uuid.UUID, counted_since: datetime | None) -> int:
        """Les échecs depuis la dernière réussite, ou depuis le dernier déblocage."""
        with self._sessions() as session:
            # La dernière réussite se repère par son numéro, croissant, et non
            # par son heure : deux tentatives peuvent avoir la même heure.
            last_success_id = session.scalar(
                select(func.max(LoginAttemptModel.id)).where(
                    LoginAttemptModel.user_id == user_id, LoginAttemptModel.success.is_(True)
                )
            )
            query = select(func.count()).where(
                LoginAttemptModel.user_id == user_id, LoginAttemptModel.success.is_(False)
            )
            if last_success_id is not None:
                query = query.where(LoginAttemptModel.id > last_success_id)
            if counted_since is not None:
                query = query.where(LoginAttemptModel.occurred_at > counted_since)
            return session.scalar(query) or 0

    # --- Sessions -------------------------------------------------------------

    def open_session(self, user_id: uuid.UUID, token_hash: str, now: datetime, expires_at: datetime) -> None:
        with self._sessions() as session:
            session.add(
                AuthSessionModel(user_id=user_id, token_hash=token_hash, last_seen_at=now, expires_at=expires_at)
            )
            session.commit()

    def use_session(self, token_hash: str, now: datetime, new_expiry: datetime) -> uuid.UUID | None:
        """Le compte d'une session ouverte et non expirée, dont l'expiration
        est repoussée ; None si la session n'est plus valable."""
        with self._sessions() as session:
            model = session.scalars(
                select(AuthSessionModel).where(
                    AuthSessionModel.token_hash == token_hash,
                    AuthSessionModel.closed_at.is_(None),
                    AuthSessionModel.expires_at > now,
                )
            ).one_or_none()
            if model is None:
                return None
            model.last_seen_at = now
            model.expires_at = new_expiry
            session.commit()
            return model.user_id

    def close_session(self, token_hash: str, now: datetime) -> None:
        with self._sessions() as session:
            session.execute(
                update(AuthSessionModel)
                .where(AuthSessionModel.token_hash == token_hash, AuthSessionModel.closed_at.is_(None))
                .values(closed_at=now)
            )
            session.commit()
