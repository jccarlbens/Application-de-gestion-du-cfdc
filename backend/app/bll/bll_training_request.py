"""Les règles des demandes de formation (US-014).

- Enregistrer : secrétaire, coordonnateur, chef de service, administrateur.
- Valider ou refuser une demande en attente : coordonnateur, administrateur ;
  un refus demande un motif. Une décision est définitive : seul
  l'administrateur la corrige, sans jamais revenir à « en attente ».
- Ajuster (tous les champs sauf le statut) : secrétaire, coordonnateur,
  administrateur, même après la décision. C'est l'une des deux exceptions
  voulues à la règle « seul l'administrateur modifie » (PRD.md §2).
- Rien ne se supprime.
"""

from collections.abc import Callable
from datetime import UTC, date, datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from app.bll.bll_training import CATALOGUE_READERS, clean
from app.bll.bll_user import audit_actor
from app.core.config import settings
from app.core.exceptions import ForbiddenError, InvalidInputError
from app.dal.dal_audit import acting_as
from app.dal.dal_training import DalTraining
from app.dal.dal_training_request import DalTrainingRequest
from app.entities.ent_training_request import EntTrainingRequest, EntTrainingRequestInput, RequestStatus
from app.entities.ent_user import EntActor, Role

SERVICE_MAX = 150
PERIOD_MAX = 100
TEXT_MAX = 2000
PARTICIPANTS_MIN, PARTICIPANTS_MAX = 1, 500

READERS = CATALOGUE_READERS
RECORDERS = frozenset({Role.SECRETARY, Role.COORDINATOR, Role.SERVICE_HEAD, Role.IT_ADMIN})
ADJUSTERS = frozenset({Role.SECRETARY, Role.COORDINATOR, Role.IT_ADMIN})
DECIDERS = frozenset({Role.COORDINATOR, Role.IT_ADMIN})


def local_today() -> date:
    """« Aujourd'hui » dans le calendrier de l'AAN, pas en UTC (E3-8)."""
    return datetime.now(ZoneInfo(settings.local_timezone)).date()


class BllTrainingRequest:
    def __init__(
        self,
        dal: DalTrainingRequest | None = None,
        trainings: DalTraining | None = None,
        today: Callable[[], date] = local_today,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._dal = dal or DalTrainingRequest()
        self._trainings = trainings or DalTraining()
        self._today = today
        self._clock = clock

    def list(self, actor: EntActor, status: str | None = None) -> list[EntTrainingRequest]:
        self._require(actor, READERS, "Votre rôle ne permet pas de voir les demandes de formation.")
        wanted = None
        if status:
            try:
                wanted = RequestStatus(status)
            except ValueError as error:
                raise InvalidInputError("Ce statut n'existe pas.") from error
        return self._dal.list(wanted)

    def get(self, actor: EntActor, request_id: UUID) -> EntTrainingRequest:
        self._require(actor, READERS, "Votre rôle ne permet pas de voir les demandes de formation.")
        return self._dal.get(request_id)

    def create(self, actor: EntActor, data: dict) -> EntTrainingRequest:
        self._require(actor, RECORDERS, "Votre rôle ne permet pas d'enregistrer une demande de formation.")
        checked = self._validate(data)
        with acting_as(audit_actor(actor)):
            return self._dal.create(checked, actor.user_id)

    def adjust(self, actor: EntActor, request_id: UUID, data: dict) -> EntTrainingRequest:
        self._require(actor, ADJUSTERS, "Votre rôle ne permet pas d'ajuster une demande de formation.")
        self._dal.get(request_id)  # 404 avant toute validation
        checked = self._validate(data)
        with acting_as(audit_actor(actor)):
            return self._dal.update(request_id, checked)

    def decide(self, actor: EntActor, request_id: UUID, status: str, reason: str | None) -> EntTrainingRequest:
        self._require(actor, DECIDERS, "Seuls le coordonnateur et l'administrateur informatique décident d'une demande.")
        try:
            decision = RequestStatus(status)
        except ValueError as error:
            raise InvalidInputError("Choisissez « validée » ou « refusée ».") from error
        if decision is RequestStatus.PENDING:
            raise InvalidInputError("Une décision ne revient pas « en attente ».")
        current = self._dal.get(request_id)
        if current.status is not RequestStatus.PENDING and Role.IT_ADMIN not in actor.roles:
            raise ForbiddenError(
                "Cette demande a déjà reçu une décision : seul l'administrateur informatique peut la corriger."
            )
        reason = (reason or "").strip() or None
        if decision is RequestStatus.REFUSED and reason is None:
            raise InvalidInputError("Un refus demande un motif.")
        if reason is not None and len(reason) > TEXT_MAX:
            raise InvalidInputError(f"Le motif ne doit pas dépasser {TEXT_MAX} caractères.")
        with acting_as(audit_actor(actor)):
            return self._dal.decide(request_id, decision, actor.user_id, reason, self._clock())

    # --- Validation -----------------------------------------------------------

    def _validate(self, data: dict) -> EntTrainingRequestInput:
        service = clean(data.get("requesting_service") or "")
        if not service:
            raise InvalidInputError("Le service demandeur est obligatoire.")
        if len(service) > SERVICE_MAX:
            raise InvalidInputError(f"Le service demandeur ne doit pas dépasser {SERVICE_MAX} caractères.")
        received_on = data.get("received_on") or self._today()
        if received_on > self._today():
            raise InvalidInputError("La date de réception ne peut pas être dans le futur.")
        participants = data.get("expected_participants")
        if not isinstance(participants, int) or not PARTICIPANTS_MIN <= participants <= PARTICIPANTS_MAX:
            raise InvalidInputError(
                f"Le nombre de participants prévu doit aller de {PARTICIPANTS_MIN} à {PARTICIPANTS_MAX}."
            )
        period = clean(data.get("desired_period") or "") or None
        if period is not None and len(period) > PERIOD_MAX:
            raise InvalidInputError(f"La période souhaitée ne doit pas dépasser {PERIOD_MAX} caractères.")
        comment = (data.get("comment") or "").strip() or None
        if comment is not None and len(comment) > TEXT_MAX:
            raise InvalidInputError(f"Le commentaire ne doit pas dépasser {TEXT_MAX} caractères.")
        training_id = data.get("training_id")
        if training_id is None or not self._trainings.training_exists(training_id):
            raise InvalidInputError("Choisissez une formation du catalogue.")
        return EntTrainingRequestInput(
            requesting_service=service,
            is_external=bool(data.get("is_external")),
            received_on=received_on,
            training_id=training_id,
            expected_participants=participants,
            desired_period=period,
            comment=comment,
        )

    @staticmethod
    def _require(actor: EntActor, roles, message: str) -> None:
        if not actor.roles & frozenset(roles):
            raise ForbiddenError(message)
