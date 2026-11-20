"""Le journal des modifications (US-003) : rien ne s'efface sans trace
(PRD.md §7).

Juste avant chaque enregistrement (`before_flush`), chaque création,
modification et suppression d'une ligne d'une table journalisée ajoute une
entrée à `audit_log`, **dans la même transaction** : la modification et sa
trace sont enregistrées ensemble, ou pas du tout.

Une table se déclare avec `__audit__ = AuditPolicy(...)`, ou s'exempte en
figurant dans `EXEMPT_TABLES`. Un test (tests/unit/test_audit_coverage.py)
échoue si une table n'est ni l'un ni l'autre : une table oubliée ne passe pas
inaperçue.
"""

import enum
import uuid
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, Index, String, column, event, func, inspect, select, table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import MANYTOONE, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.orm.attributes import NO_VALUE

from app.dal.database import Base, SessionLocal
from app.entities.ent_audit import (
    SECRET_CHANGED,
    SECRET_SET,
    AuditAction,
    EntAuditActor,
    EntAuditEntry,
)

# Tables délibérément non journalisées, avec leur raison.
EXEMPT_TABLES = {
    "audit_log": "le journal lui-même",
    "password_tokens": "des liens secrets à usage unique ; le mot de passe choisi est journalisé sur le compte",
    "alembic_version": "la version du schéma, tenue par Alembic",
    "login_attempts": "les tentatives de connexion : un journal à part, qui ne se modifie pas (US-004)",
    "auth_sessions": "les sessions de connexion, prolongées à chaque requête ; jetons secrets (US-004)",
}


@dataclass(frozen=True)
class AuditPolicy:
    """Comment une table est journalisée.

    `subject` donne la fiche dont l'historique reçoit l'entrée : un rôle se
    journalise sous son compte. `secret` : jamais recopiés. `personal` :
    gardés, mais masqués à la lecture pour les rôles qui ne les voient pas.
    """

    subject: Callable[[Any], tuple[str, Any]]
    secret: frozenset[str] = field(default_factory=frozenset)
    personal: frozenset[str] = field(default_factory=frozenset)


class MissingAuditActorError(RuntimeError):
    """Une modification journalisée sans auteur déclaré : un oubli de code."""


class AuditLogModel(Base):
    __tablename__ = "audit_log"
    __table_args__ = (Index("ix_audit_log_subject", "subject_type", "subject_id"),)

    # Un numéro croissant : toutes les entrées d'une transaction ont la même
    # heure, le numéro garde leur ordre exact.
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column()
    actor_label: Mapped[str] = mapped_column(String(120))
    subject_type: Mapped[str] = mapped_column(String(50))
    subject_id: Mapped[str] = mapped_column(String(64))
    table_name: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(10))
    before: Mapped[dict | None] = mapped_column(JSONB)
    after: Mapped[dict | None] = mapped_column(JSONB)


# --- L'auteur courant ---------------------------------------------------------

_current_actor: ContextVar[EntAuditActor | None] = ContextVar("audit_actor", default=None)


@contextmanager
def acting_as(actor: EntAuditActor) -> Iterator[None]:
    """Déclare l'auteur des modifications faites dans ce bloc."""
    token = _current_actor.set(actor)
    try:
        yield
    finally:
        _current_actor.reset(token)


# --- La capture -----------------------------------------------------------------


def _json(value: Any) -> Any:
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, enum.Enum):
        return value.value
    return value


def _columns(obj: Any) -> list[str]:
    return [attr.key for attr in inspect(obj).mapper.column_attrs]


def _snapshot(obj: Any, policy: AuditPolicy, previous: bool) -> dict[str, Any]:
    state = inspect(obj)
    values: dict[str, Any] = {}
    for key in _columns(obj):
        current = getattr(obj, key)
        value = current
        if previous:
            old = state.committed_state.get(key, NO_VALUE)
            value = current if old is NO_VALUE else old
        if key in policy.secret:
            changed = key in state.committed_state and state.committed_state[key] != current
            value = None if value is None else (SECRET_CHANGED if changed and not previous else SECRET_SET)
        values[key] = _json(value)
    return values


def _entry(obj: Any, action: AuditAction, actor: EntAuditActor) -> AuditLogModel:
    policy: AuditPolicy = type(obj).__audit__
    subject_type, subject_id = policy.subject(obj)
    return AuditLogModel(
        actor_user_id=actor.user_id,
        actor_label=actor.label,
        subject_type=subject_type,
        subject_id=str(subject_id),
        table_name=type(obj).__tablename__,
        action=action.value,
        before=None if action is AuditAction.CREATE else _snapshot(obj, policy, previous=True),
        after=None if action is AuditAction.DELETE else _snapshot(obj, policy, previous=False),
    )


def _is_audited(obj: Any) -> bool:
    return getattr(type(obj), "__audit__", None) is not None


@event.listens_for(Session, "before_flush")
def _record_changes(session: Session, flush_context, instances) -> None:
    new = [o for o in session.new if _is_audited(o)]
    dirty = [o for o in session.dirty if _is_audited(o) and session.is_modified(o, include_collections=False)]
    deleted = [o for o in session.deleted if _is_audited(o)]
    if not (new or dirty or deleted):
        return
    actor = _current_actor.get()
    if actor is None:
        raise MissingAuditActorError("Aucun auteur déclaré pour le journal : entourez l'opération de acting_as().")
    # Les identifiants sont attribués tout de suite, pour que l'entrée nomme
    # la fiche créée (un rôle nomme son compte).
    for obj in new:
        if getattr(obj, "id", None) is None:
            obj.id = uuid.uuid4()
    # Une clé étrangère donnée par un objet (`module=…`, `user=…`) n'est remplie
    # par SQLAlchemy qu'au moment de l'écriture, après cette photo : on la
    # recopie d'abord, sinon l'entrée garderait une clé vide (constaté sur
    # US-012 : `module_id`, et `user_id` des rôles depuis US-003).
    for obj in new:
        _fill_foreign_keys(obj)
    # Un ordre lisible et toujours le même (SQLAlchemy ne garantit aucun ordre) :
    # les retraits, puis les modifications, puis les ajouts ; une fiche avant
    # ses dépendances (un compte avant ses rôles), dans l'ordre des tables.
    entries = (
        [_entry(o, AuditAction.DELETE, actor) for o in sorted(deleted, key=_table_rank, reverse=True)]
        + [_entry(o, AuditAction.UPDATE, actor) for o in sorted(dirty, key=_table_rank)]
        + [_entry(o, AuditAction.CREATE, actor) for o in sorted(new, key=_table_rank)]
    )
    session.add_all(entries)


def _fill_foreign_keys(obj: Any) -> None:
    state = inspect(obj)
    for relationship in state.mapper.relationships:
        if relationship.direction is not MANYTOONE:
            continue
        related = state.attrs[relationship.key].loaded_value
        if related is None or related is NO_VALUE:
            continue
        for local, remote in relationship.local_remote_pairs:
            key = state.mapper.get_property_by_column(local).key
            if getattr(obj, key) is None:
                setattr(obj, key, getattr(related, inspect(related).mapper.get_property_by_column(remote).key))


def _table_rank(obj: Any) -> tuple[int, str]:
    tables = [table.name for table in Base.metadata.sorted_tables]
    name = type(obj).__tablename__
    return (tables.index(name), str(getattr(obj, "id", "")))


# --- La lecture -------------------------------------------------------------------


def _to_entity(model: AuditLogModel, actor_name: str | None = None) -> EntAuditEntry:
    return EntAuditEntry(
        occurred_at=model.occurred_at,
        actor_user_id=model.actor_user_id,
        actor_label=model.actor_label,
        subject_type=model.subject_type,
        subject_id=model.subject_id,
        table_name=model.table_name,
        action=AuditAction(model.action),
        before=model.before,
        after=model.after,
        actor_name=actor_name,
    )


def personal_fields(table_name: str) -> frozenset[str]:
    """Les champs personnels d'une table, à masquer à la lecture."""
    for mapper in Base.registry.mappers:
        cls = mapper.class_
        if getattr(cls, "__tablename__", None) == table_name and _is_audited_class(cls):
            return cls.__audit__.personal
    return frozenset()


def _is_audited_class(cls: type) -> bool:
    return getattr(cls, "__audit__", None) is not None


class DalAudit:
    def __init__(self, session_factory: sessionmaker[Session] = SessionLocal) -> None:
        self._sessions = session_factory

    def history(self, subject_type: str, subject_id: str) -> list[EntAuditEntry]:
        """L'historique d'une fiche, dans l'ordre, avec le nom de chaque auteur
        lu dans `users` (le journal ne dépend pas de la DAL des comptes)."""
        name = (_USERS.c.first_name + " " + _USERS.c.last_name + " (" + _USERS.c.badge + ")").label("actor_name")
        with self._sessions() as session:
            rows = session.execute(
                select(AuditLogModel, name)
                .outerjoin(_USERS, _USERS.c.id == AuditLogModel.actor_user_id)
                .where(AuditLogModel.subject_type == subject_type, AuditLogModel.subject_id == subject_id)
                .order_by(AuditLogModel.id)
            )
            return [_to_entity(model, actor_name) for model, actor_name in rows]


# Juste ce qu'il faut de la table des comptes pour nommer un auteur.
_USERS = table(
    "users", column("id"), column("first_name", String), column("last_name", String), column("badge", String)
)
