"""Les règles du catalogue des formations (US-010).

- Enregistrer une formation : secrétaire, coordonnateur, chef de service du
  CFDC, administrateur (PRD.md §5).
- La modifier : l'administrateur seulement, en attendant les demandes de
  correction de l'Epic 5 (affinage de l'Epic 2, Q4).
- Ajouter ou renommer un domaine ou un sous-domaine : l'administrateur seulement.
- Ajouter un module, désigner le formateur d'un module « à désigner » : ceux
  qui enregistrent les formations ; changer un formateur déjà désigné, ou le
  titre d'un module : l'administrateur seulement (US-011, décision 1A).
- Rien ne se supprime.
"""

import re
from uuid import UUID

from app.bll.bll_user import audit_actor
from app.core.exceptions import DuplicateNameError, ForbiddenError, InvalidInputError, RecordNotFoundError
from app.dal.dal_audit import acting_as
from app.dal.dal_training import DalTraining
from app.entities.ent_training import (
    EntDomain,
    EntModule,
    EntModuleInput,
    EntSubdomain,
    EntTrainer,
    EntTraining,
    EntTrainingInput,
)
from app.entities.ent_user import EntActor, Role

TITLE_MAX = 200
DESCRIPTION_MAX = 2000
NAME_MAX = 100

# Qui voit le catalogue : tous les rôles sauf le formateur (PRD.md §5).
CATALOGUE_READERS = frozenset(Role) - {Role.TRAINER}
# Qui enregistre une formation (PRD.md §5) : la direction consulte seulement.
TRAINING_WRITERS = frozenset({Role.SECRETARY, Role.COORDINATOR, Role.SERVICE_HEAD, Role.IT_ADMIN})

_SPACES = re.compile(r"\s+")


def clean(text: str) -> str:
    """Le texte saisi, sans espaces au début, à la fin, ni en double."""
    return _SPACES.sub(" ", text).strip()


def title_key(title: str) -> str:
    """Ce qui rend deux intitulés identiques : ni les majuscules ni les espaces
    en trop ne comptent ; les accents, si (US-010, décision 2)."""
    return clean(title).casefold()


class BllTraining:
    def __init__(self, dal: DalTraining | None = None) -> None:
        self._dal = dal or DalTraining()

    # --- Domaines et sous-domaines -------------------------------------------

    def list_domains(self, actor: EntActor) -> list[EntDomain]:
        self._require(actor, CATALOGUE_READERS, "Votre rôle ne permet pas de voir le catalogue.")
        return self._dal.list_domains()

    def add_domain(self, actor: EntActor, name: str) -> EntDomain:
        self._require_admin(actor)
        name = self._name(name, "domaine")
        self._refuse_taken(name, [d.name for d in self._dal.list_domains()], "Un domaine porte déjà ce nom.")
        with acting_as(audit_actor(actor)):
            return self._dal.add_domain(name)

    def rename_domain(self, actor: EntActor, domain_id: UUID, name: str) -> EntDomain:
        self._require_admin(actor)
        name = self._name(name, "domaine")
        others = [d.name for d in self._dal.list_domains() if d.id != domain_id]
        self._refuse_taken(name, others, "Un domaine porte déjà ce nom.")
        with acting_as(audit_actor(actor)):
            return self._dal.rename_domain(domain_id, name)

    def add_subdomain(self, actor: EntActor, domain_id: UUID, name: str) -> EntSubdomain:
        self._require_admin(actor)
        name = self._name(name, "sous-domaine")
        domain = self._domain(domain_id)
        self._refuse_taken(name, [s.name for s in domain.subdomains], "Ce domaine a déjà un sous-domaine de ce nom.")
        with acting_as(audit_actor(actor)):
            return self._dal.add_subdomain(domain_id, name)

    def rename_subdomain(self, actor: EntActor, subdomain_id: UUID, name: str) -> EntSubdomain:
        self._require_admin(actor)
        name = self._name(name, "sous-domaine")
        domain = next((d for d in self._dal.list_domains() if any(s.id == subdomain_id for s in d.subdomains)), None)
        if domain is None:
            raise RecordNotFoundError("Ce sous-domaine n'existe pas.")
        others = [s.name for s in domain.subdomains if s.id != subdomain_id]
        self._refuse_taken(name, others, "Ce domaine a déjà un sous-domaine de ce nom.")
        with acting_as(audit_actor(actor)):
            return self._dal.rename_subdomain(subdomain_id, name)

    # --- Formations -----------------------------------------------------------

    def list_trainings(self, actor: EntActor) -> list[EntTraining]:
        self._require(actor, CATALOGUE_READERS, "Votre rôle ne permet pas de voir le catalogue.")
        return sorted(
            self._dal.list_trainings(),
            key=lambda t: (t.domain_name.casefold(), t.subdomain_name.casefold(), t.title.casefold()),
        )

    def get_training(self, actor: EntActor, training_id: UUID) -> EntTraining:
        self._require(actor, CATALOGUE_READERS, "Votre rôle ne permet pas de voir le catalogue.")
        return self._dal.get_training(training_id)

    def create_training(
        self, actor: EntActor, title: str, description: str | None, subdomain_id: UUID
    ) -> EntTraining:
        self._require(actor, TRAINING_WRITERS, "Votre rôle ne permet pas d'enregistrer une formation.")
        training = self._validate(title, description, subdomain_id)
        with acting_as(audit_actor(actor)):
            return self._dal.create_training(training)

    def update_training(
        self, actor: EntActor, training_id: UUID, title: str, description: str | None, subdomain_id: UUID
    ) -> EntTraining:
        self._require(
            actor,
            {Role.IT_ADMIN},
            "Seul l'administrateur informatique modifie une formation enregistrée ; "
            "les autres feront une demande de correction.",
        )
        self._dal.get_training(training_id)  # 404 avant toute validation
        training = self._validate(title, description, subdomain_id)
        with acting_as(audit_actor(actor)):
            return self._dal.update_training(training_id, training)

    # --- Modules et formateurs (US-011) ------------------------------------------

    def list_modules(self, actor: EntActor, training_id: UUID) -> list[EntModule]:
        self._require(actor, CATALOGUE_READERS, "Votre rôle ne permet pas de voir le catalogue.")
        self._dal.get_training(training_id)  # 404 si la formation n'existe pas
        return self._dal.list_modules(training_id)

    def list_trainers(self, actor: EntActor) -> list[EntTrainer]:
        """Les formateurs qu'on peut désigner : comptes actifs au rôle formateur."""
        self._require(actor, TRAINING_WRITERS, "Votre rôle ne permet pas de désigner un formateur.")
        return self._dal.list_active_trainers()

    def add_module(
        self, actor: EntActor, training_id: UUID, title: str, description: str | None, trainer_id: UUID | None
    ) -> EntModule:
        self._require(actor, TRAINING_WRITERS, "Votre rôle ne permet pas d'ajouter un module.")
        self._dal.get_training(training_id)
        module = self._validate_module(title, description, trainer_id)
        with acting_as(audit_actor(actor)):
            return self._dal.add_module(training_id, module)

    def assign_trainer(self, actor: EntActor, module_id: UUID, trainer_id: UUID) -> EntModule:
        """Désigner le formateur d'un module « à désigner » est un complément ;
        changer un formateur déjà désigné, une modification (décision 1A)."""
        self._require(actor, TRAINING_WRITERS, "Votre rôle ne permet pas de désigner un formateur.")
        module = self._dal.get_module(module_id)
        if module.trainer is not None and Role.IT_ADMIN not in actor.roles:
            raise ForbiddenError(
                "Ce module a déjà un formateur : seul l'administrateur informatique peut le changer."
            )
        self._check_trainer(trainer_id)
        changed = EntModuleInput(module.title, title_key(module.title), module.description, trainer_id)
        with acting_as(audit_actor(actor)):
            return self._dal.update_module(module_id, changed)

    def update_module(
        self, actor: EntActor, module_id: UUID, title: str, description: str | None, trainer_id: UUID | None
    ) -> EntModule:
        self._require(
            actor,
            {Role.IT_ADMIN},
            "Seul l'administrateur informatique modifie un module enregistré ; "
            "les autres feront une demande de correction.",
        )
        current = self._dal.get_module(module_id)
        # Garder le même formateur reste permis même s'il a quitté ce rôle
        # (décision 4A) : seul un nouveau formateur doit être actif et formateur.
        same_trainer = current.trainer is not None and current.trainer.id == trainer_id
        module = self._validate_module(title, description, None if same_trainer else trainer_id)
        if same_trainer:
            module = EntModuleInput(module.title, module.title_key, module.description, trainer_id)
        with acting_as(audit_actor(actor)):
            return self._dal.update_module(module_id, module)

    def _validate_module(self, title: str, description: str | None, trainer_id: UUID | None) -> EntModuleInput:
        title = clean(title)
        if not title:
            raise InvalidInputError("Le titre du module est obligatoire.")
        if len(title) > TITLE_MAX:
            raise InvalidInputError(f"Le titre du module ne doit pas dépasser {TITLE_MAX} caractères.")
        description = (description or "").strip() or None
        if description is not None and len(description) > DESCRIPTION_MAX:
            raise InvalidInputError(f"La description ne doit pas dépasser {DESCRIPTION_MAX} caractères.")
        if trainer_id is not None:
            self._check_trainer(trainer_id)
        return EntModuleInput(title, title_key(title), description, trainer_id)

    def _check_trainer(self, trainer_id: UUID) -> None:
        trainer = self._dal.get_trainer(trainer_id)
        if trainer is None or not trainer.is_trainer:
            raise InvalidInputError("Choisissez un formateur de la liste : ce compte n'a pas le rôle de formateur.")
        if not trainer.is_active:
            raise InvalidInputError("Ce compte de formateur est désactivé : choisissez-en un autre.")

    # --- Validation -----------------------------------------------------------

    def _validate(self, title: str, description: str | None, subdomain_id: UUID) -> EntTrainingInput:
        title = clean(title)
        if not title:
            raise InvalidInputError("L'intitulé est obligatoire.")
        if len(title) > TITLE_MAX:
            raise InvalidInputError(f"L'intitulé ne doit pas dépasser {TITLE_MAX} caractères.")
        description = (description or "").strip() or None
        if description is not None and len(description) > DESCRIPTION_MAX:
            raise InvalidInputError(f"La description ne doit pas dépasser {DESCRIPTION_MAX} caractères.")
        if not self._dal.subdomain_exists(subdomain_id):
            raise InvalidInputError("Choisissez un sous-domaine de la liste.")
        return EntTrainingInput(title, title_key(title), description, subdomain_id)

    @staticmethod
    def _name(name: str, kind: str) -> str:
        name = clean(name)
        if not name:
            raise InvalidInputError(f"Le nom du {kind} est obligatoire.")
        if len(name) > NAME_MAX:
            raise InvalidInputError(f"Le nom du {kind} ne doit pas dépasser {NAME_MAX} caractères.")
        return name

    @staticmethod
    def _refuse_taken(name: str, taken: list[str], message: str) -> None:
        if title_key(name) in {title_key(t) for t in taken}:
            raise DuplicateNameError(message)

    def _domain(self, domain_id: UUID) -> EntDomain:
        domain = next((d for d in self._dal.list_domains() if d.id == domain_id), None)
        if domain is None:
            raise RecordNotFoundError("Ce domaine n'existe pas.")
        return domain

    @staticmethod
    def _require(actor: EntActor, roles, message: str) -> None:
        if not actor.roles & frozenset(roles):
            raise ForbiddenError(message)

    def _require_admin(self, actor: EntActor) -> None:
        self._require(actor, {Role.IT_ADMIN}, "Seul l'administrateur informatique gère les domaines et sous-domaines.")
