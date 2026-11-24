"""Les règles des sessions de formation (US-015).

- Planifier, reporter, annuler : coordonnateur et administrateur (PRD.md §5).
  Reporter et annuler sont l'autre exception voulue à la règle « seul
  l'administrateur modifie » (PRD.md §2).
- Une session rattachée à une demande vise une demande **validée**, et prend
  sa formation.
- Durée indéterminée : la fin ne précède pas le début ; les dates passées sont
  permises, pour enregistrer une formation déjà donnée.
- « Terminée » se déduit : date de fin passée dans le calendrier de l'AAN.
  Une session terminée ne se reporte plus, et une session annulée ne revient
  pas à « planifiée » : seul l'administrateur corrige.
"""

from collections.abc import Callable
from datetime import date
from uuid import UUID

from app.bll.bll_training import CATALOGUE_READERS, clean
from app.bll.bll_training_request import local_today
from app.bll.bll_user import audit_actor
from app.core.exceptions import ForbiddenError, InvalidInputError
from app.dal.dal_audit import acting_as
from app.dal.dal_training import DalTraining
from app.dal.dal_training_request import DalTrainingRequest
from app.dal.dal_training_session import DalTrainingSession
from app.entities.ent_training_request import RequestStatus
from app.entities.ent_training_session import EntTrainingSession, SessionStatus
from app.entities.ent_user import EntActor, Role

LABEL_MAX = 100
REASON_MAX = 2000

READERS = CATALOGUE_READERS
PLANNERS = frozenset({Role.COORDINATOR, Role.IT_ADMIN})


class BllTrainingSession:
    def __init__(
        self,
        dal: DalTrainingSession | None = None,
        trainings: DalTraining | None = None,
        requests: DalTrainingRequest | None = None,
        today: Callable[[], date] = local_today,
    ) -> None:
        self._dal = dal or DalTrainingSession()
        self._trainings = trainings or DalTraining()
        self._requests = requests or DalTrainingRequest()
        self._today = today

    def today(self) -> date:
        return self._today()

    # --- Lecture --------------------------------------------------------------

    def list(self, actor: EntActor, training_id: UUID | None = None, request_id: UUID | None = None) -> list[EntTrainingSession]:
        """À venir d'abord (les plus proches en tête), puis les passées, les plus
        récentes en tête (US-015, décision 7A)."""
        self._require(actor, READERS, "Votre rôle ne permet pas de voir les sessions.")
        today = self._today()
        sessions = self._dal.list(training_id=training_id, request_id=request_id)
        coming = [s for s in sessions if s.ends_on >= today]
        past = sorted((s for s in sessions if s.ends_on < today), key=lambda s: s.starts_on, reverse=True)
        return coming + past

    def get(self, actor: EntActor, session_id: UUID) -> EntTrainingSession:
        self._require(actor, READERS, "Votre rôle ne permet pas de voir les sessions.")
        return self._dal.get(session_id)

    # --- Écriture --------------------------------------------------------------

    def plan(
        self, actor: EntActor, training_id: UUID | None, request_id: UUID | None, label: str | None,
        starts_on: date | None, ends_on: date | None,
    ) -> EntTrainingSession:
        self._require(actor, PLANNERS, "Seuls le coordonnateur et l'administrateur informatique planifient une session.")
        if request_id is not None:
            request = self._requests.get(request_id)
            if request.status is not RequestStatus.APPROVED:
                raise InvalidInputError("Une session ne répond qu'à une demande validée.")
            # La session prend la formation de la demande (US-015, décision 1).
            if training_id is not None and training_id != request.training_id:
                raise InvalidInputError("Une session rattachée à une demande porte la formation de cette demande.")
            training_id = request.training_id
        if training_id is None or not self._trainings.training_exists(training_id):
            raise InvalidInputError("Choisissez une formation du catalogue.")
        starts_on, ends_on = self._dates(starts_on, ends_on)
        with acting_as(audit_actor(actor)):
            return self._dal.create(training_id, request_id, self._label(label), starts_on, ends_on, actor.user_id)

    def reschedule(self, actor: EntActor, session_id: UUID, starts_on: date | None, ends_on: date | None) -> EntTrainingSession:
        self._require(actor, PLANNERS, "Seuls le coordonnateur et l'administrateur informatique reportent une session.")
        current = self._dal.get(session_id)
        admin = Role.IT_ADMIN in actor.roles
        if current.status is SessionStatus.CANCELLED:
            raise InvalidInputError("Cette session est annulée : remettez-la d'abord en « planifiée ».")
        if current.is_finished(self._today()) and not admin:
            raise ForbiddenError("Cette session est terminée : seul l'administrateur informatique peut changer ses dates.")
        starts_on, ends_on = self._dates(starts_on, ends_on)
        with acting_as(audit_actor(actor)):
            return self._dal.update(session_id, starts_on=starts_on, ends_on=ends_on)

    def cancel(self, actor: EntActor, session_id: UUID, reason: str | None) -> EntTrainingSession:
        self._require(actor, PLANNERS, "Seuls le coordonnateur et l'administrateur informatique annulent une session.")
        current = self._dal.get(session_id)
        if current.status is SessionStatus.CANCELLED:
            raise InvalidInputError("Cette session est déjà annulée.")
        reason = (reason or "").strip()
        if not reason:
            raise InvalidInputError("Une annulation demande un motif.")
        if len(reason) > REASON_MAX:
            raise InvalidInputError(f"Le motif ne doit pas dépasser {REASON_MAX} caractères.")
        with acting_as(audit_actor(actor)):
            return self._dal.update(session_id, status=SessionStatus.CANCELLED.value, cancel_reason=reason)

    def restore(self, actor: EntActor, session_id: UUID) -> EntTrainingSession:
        """Corriger une annulation faite par erreur : l'administrateur seul."""
        self._require(actor, {Role.IT_ADMIN}, "Seul l'administrateur informatique remet une session annulée en « planifiée ».")
        current = self._dal.get(session_id)
        if current.status is not SessionStatus.CANCELLED:
            raise InvalidInputError("Cette session n'est pas annulée.")
        with acting_as(audit_actor(actor)):
            return self._dal.update(session_id, status=SessionStatus.PLANNED.value, cancel_reason=None)

    # --- Validation -----------------------------------------------------------

    @staticmethod
    def _dates(starts_on: date | None, ends_on: date | None) -> tuple[date, date]:
        if starts_on is None or ends_on is None:
            raise InvalidInputError("Les dates de début et de fin sont obligatoires.")
        if ends_on < starts_on:
            raise InvalidInputError("La date de fin ne peut pas précéder la date de début.")
        return starts_on, ends_on

    @staticmethod
    def _label(label: str | None) -> str | None:
        label = clean(label or "") or None
        if label is not None and len(label) > LABEL_MAX:
            raise InvalidInputError(f"Le libellé ne doit pas dépasser {LABEL_MAX} caractères.")
        return label

    @staticmethod
    def _require(actor: EntActor, roles, message: str) -> None:
        if not actor.roles & frozenset(roles):
            raise ForbiddenError(message)
