from dataclasses import replace

from app.core.exceptions import ForbiddenError, RecordNotFoundError
from app.dal.dal_audit import DalAudit, personal_fields
from app.entities.ent_audit import MASKED, EntAuditEntry
from app.entities.ent_user import EntActor, Role

# Qui voit l'historique de quel genre de fiche : les mêmes rôles que ceux qui
# voient la fiche (PRD.md §5). Chaque Epic ajoute ses fiches ici.
_CATALOGUE = frozenset(Role) - {Role.TRAINER}
_READERS = {
    "users": frozenset({Role.IT_ADMIN, Role.COORDINATOR}),
    # Le catalogue (US-010) : tous ceux qui voient la fiche.
    "trainings": _CATALOGUE,
    "domains": _CATALOGUE,
    "subdomains": _CATALOGUE,
    # Les demandes de formation (US-014) : tous ceux qui les voient.
    "training_requests": _CATALOGUE,
    # Les sessions de formation (US-015).
    "training_sessions": _CATALOGUE,
}

# Les genres de fiches qui ont un historique, et qui peut lire au moins l'un
# d'eux : la route se protège avec cette liste, la BLL vérifie le genre.
SUBJECT_TYPES = frozenset(_READERS)
ANY_READER = frozenset().union(*_READERS.values())

# Les seuls rôles qui voient les données personnelles (PRD.md §7).
_SEES_PERSONAL_DATA = frozenset({Role.IT_ADMIN, Role.COORDINATOR})


def _mask(values: dict | None, fields: frozenset[str]) -> dict | None:
    if values is None:
        return None
    return {key: (MASKED if key in fields and value is not None else value) for key, value in values.items()}


class BllHistory:
    def __init__(self, dal: DalAudit | None = None) -> None:
        self._dal = dal or DalAudit()

    def history(self, actor: EntActor, subject_type: str, subject_id: str) -> list[EntAuditEntry]:
        readers = _READERS.get(subject_type)
        if readers is None:
            raise RecordNotFoundError("Ce genre de fiche n'a pas d'historique.")
        if not actor.roles & readers:
            raise ForbiddenError("Votre rôle ne permet pas de voir cet historique.")
        entries = self._dal.history(subject_type, subject_id)
        if actor.roles & _SEES_PERSONAL_DATA:
            return entries
        return [self._masked(entry) for entry in entries]

    def _masked(self, entry: EntAuditEntry) -> EntAuditEntry:
        fields = personal_fields(entry.table_name)
        if not fields:
            return entry
        return replace(entry, before=_mask(entry.before, fields), after=_mask(entry.after, fields))
