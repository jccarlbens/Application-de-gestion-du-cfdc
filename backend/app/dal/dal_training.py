"""Le catalogue des formations (US-010) : domaines, sous-domaines, formations.

Les trois tables sont journalisées (US-003). Rien ne s'y supprime : on ajoute,
et l'administrateur modifie.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship, selectinload, sessionmaker

from app.core.exceptions import DuplicateNameError, RecordNotFoundError
from app.dal.dal_audit import AuditPolicy
from app.dal.database import Base, SessionLocal
from app.entities.ent_training import EntDomain, EntSubdomain, EntTraining, EntTrainingInput


class DomainModel(Base):
    __tablename__ = "domains"
    __audit__ = AuditPolicy(subject=lambda domain: ("domains", domain.id))

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    subdomains: Mapped[list["SubdomainModel"]] = relationship(back_populates="domain", lazy="selectin")


class SubdomainModel(Base):
    __tablename__ = "subdomains"
    __table_args__ = (UniqueConstraint("domain_id", "name", name="uq_subdomains_domain_id_name"),)
    __audit__ = AuditPolicy(subject=lambda subdomain: ("subdomains", subdomain.id))

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    domain_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("domains.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    domain: Mapped[DomainModel] = relationship(back_populates="subdomains")


class TrainingModel(Base):
    __tablename__ = "trainings"
    __audit__ = AuditPolicy(subject=lambda training: ("trainings", training.id))

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200))
    # L'intitulé sans majuscules ni espaces en trop : deux formations ne
    # peuvent pas avoir le même (US-010, décision 2).
    title_key: Mapped[str] = mapped_column(String(200), unique=True)
    description: Mapped[str | None] = mapped_column(String(2000))
    subdomain_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subdomains.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    subdomain: Mapped[SubdomainModel] = relationship(lazy="joined")


def _subdomain(model: SubdomainModel) -> EntSubdomain:
    return EntSubdomain(id=model.id, domain_id=model.domain_id, name=model.name)


def _domain(model: DomainModel) -> EntDomain:
    subdomains = sorted(model.subdomains, key=lambda s: s.name.casefold())
    return EntDomain(id=model.id, name=model.name, subdomains=tuple(_subdomain(s) for s in subdomains))


def _training(model: TrainingModel) -> EntTraining:
    return EntTraining(
        id=model.id,
        title=model.title,
        description=model.description,
        subdomain_id=model.subdomain_id,
        subdomain_name=model.subdomain.name,
        domain_id=model.subdomain.domain_id,
        domain_name=model.subdomain.domain.name,
        created_at=model.created_at,
    )


_DUPLICATES = {
    "trainings_title_key_key": "Une formation porte déjà cet intitulé.",
    "domains_name_key": "Un domaine porte déjà ce nom.",
    "uq_subdomains_domain_id_name": "Ce domaine a déjà un sous-domaine de ce nom.",
}


def _commit(session: Session) -> None:
    """Enregistre ; un nom ou un intitulé déjà pris devient un message clair."""
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        message = str(error.orig)
        for constraint, text in _DUPLICATES.items():
            if constraint in message:
                raise DuplicateNameError(text) from error
        raise


class DalTraining:
    def __init__(self, session_factory: sessionmaker[Session] = SessionLocal) -> None:
        self._sessions = session_factory

    # --- Domaines et sous-domaines -------------------------------------------

    def list_domains(self) -> list[EntDomain]:
        with self._sessions() as session:
            models = session.scalars(select(DomainModel).options(selectinload(DomainModel.subdomains)))
            return sorted((_domain(m) for m in models), key=lambda d: d.name.casefold())

    def add_domain(self, name: str) -> EntDomain:
        with self._sessions() as session:
            model = DomainModel(name=name)
            session.add(model)
            _commit(session)
            session.refresh(model)
            return _domain(model)

    def rename_domain(self, domain_id: uuid.UUID, name: str) -> EntDomain:
        with self._sessions() as session:
            model = self._get(session, DomainModel, domain_id, "Ce domaine n'existe pas.")
            model.name = name
            _commit(session)
            session.refresh(model)
            return _domain(model)

    def add_subdomain(self, domain_id: uuid.UUID, name: str) -> EntSubdomain:
        with self._sessions() as session:
            self._get(session, DomainModel, domain_id, "Ce domaine n'existe pas.")
            model = SubdomainModel(domain_id=domain_id, name=name)
            session.add(model)
            _commit(session)
            return _subdomain(model)

    def rename_subdomain(self, subdomain_id: uuid.UUID, name: str) -> EntSubdomain:
        with self._sessions() as session:
            model = self._get(session, SubdomainModel, subdomain_id, "Ce sous-domaine n'existe pas.")
            model.name = name
            _commit(session)
            return _subdomain(model)

    def subdomain_exists(self, subdomain_id: uuid.UUID) -> bool:
        with self._sessions() as session:
            return session.get(SubdomainModel, subdomain_id) is not None

    # --- Formations -----------------------------------------------------------

    def list_trainings(self) -> list[EntTraining]:
        with self._sessions() as session:
            models = session.scalars(select(TrainingModel))
            return [_training(m) for m in models]

    def get_training(self, training_id: uuid.UUID) -> EntTraining:
        with self._sessions() as session:
            return _training(self._get(session, TrainingModel, training_id, "Cette formation n'existe pas."))

    def create_training(self, training: EntTrainingInput) -> EntTraining:
        with self._sessions() as session:
            model = TrainingModel(
                title=training.title,
                title_key=training.title_key,
                description=training.description,
                subdomain_id=training.subdomain_id,
            )
            session.add(model)
            _commit(session)
            session.refresh(model)
            return _training(model)

    def update_training(self, training_id: uuid.UUID, training: EntTrainingInput) -> EntTraining:
        """Une modification ordinaire, champ par champ, que le journal voit."""
        with self._sessions() as session:
            model = self._get(session, TrainingModel, training_id, "Cette formation n'existe pas.")
            model.title = training.title
            model.title_key = training.title_key
            model.description = training.description
            model.subdomain_id = training.subdomain_id
            _commit(session)
            session.refresh(model)
            return _training(model)

    @staticmethod
    def _get(session: Session, model_class, record_id: uuid.UUID, missing: str):
        model = session.get(model_class, record_id)
        if model is None:
            raise RecordNotFoundError(missing)
        return model
