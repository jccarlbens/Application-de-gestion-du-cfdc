"""Les règles des documents de cours (US-012).

- Déposer et remplacer : l'administrateur informatique (PRD.md §5).
- Ouvrir un document en vigueur : le formateur **actuel** du module et
  l'administrateur ; une version remplacée : l'administrateur seulement
  (affinage de l'Epic 2, Q6 et Q9 ; US-012, décision 7).
- Voir la liste : tous ceux qui voient la fiche de la formation (décision 2).
- Un fichier n'est accepté que si son contenu correspond à son extension.
"""

import io
import zipfile
from pathlib import Path, PurePath
from uuid import UUID

from app.bll.bll_training import CATALOGUE_READERS
from app.bll.bll_user import audit_actor
from app.core.config import settings
from app.core.exceptions import ForbiddenError, InvalidInputError, RecordNotFoundError
from app.dal.dal_audit import acting_as
from app.dal.dal_document import DalDocument
from app.entities.ent_document import EntDocument, EntNewDocument
from app.entities.ent_user import EntActor, Role

NAME_MAX = 200

# Extension → type du fichier, et la vérification de son contenu.
_PDF = "application/pdf"
_TYPES = {
    ".pdf": _PDF,
    ".doc": "application/msword",
    ".ppt": "application/vnd.ms-powerpoint",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}
# L'en-tête des anciens documents Office (OLE2), commun à Word et PowerPoint
# (US-012, décision 6).
_OLE2 = bytes.fromhex("D0CF11E0A1B11AE1")
_OOXML_FOLDER = {".docx": "word/", ".pptx": "ppt/"}

FORMAT_REFUSED = "Format refusé : seuls les PDF, Word (.doc, .docx) et PowerPoint (.ppt, .pptx) sont acceptés."


def _content_matches(extension: str, content: bytes) -> bool:
    if extension == ".pdf":
        return content.startswith(b"%PDF")
    if extension in (".doc", ".ppt"):
        return content.startswith(_OLE2)
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            return any(name.startswith(_OOXML_FOLDER[extension]) for name in archive.namelist())
    except zipfile.BadZipFile:
        return False


def check_file(file_name: str, content: bytes, max_bytes: int | None = None) -> EntNewDocument:
    """Le fichier, s'il est d'un format accepté et que son contenu le confirme."""
    max_bytes = max_bytes or settings.document_max_bytes
    # Seul le nom, jamais un chemin envoyé par le navigateur.
    name = PurePath(file_name.replace("\\", "/")).name.strip()
    if not name:
        raise InvalidInputError("Le fichier n'a pas de nom.")
    if len(name) > NAME_MAX:
        raise InvalidInputError(f"Le nom du fichier ne doit pas dépasser {NAME_MAX} caractères.")
    if not content:
        raise InvalidInputError("Le fichier est vide.")
    if len(content) > max_bytes:
        raise InvalidInputError(f"Le fichier dépasse {max_bytes // (1024 * 1024)} Mo.")
    extension = Path(name).suffix.lower()
    if extension not in _TYPES:
        raise InvalidInputError(FORMAT_REFUSED)
    if not _content_matches(extension, content):
        raise InvalidInputError(
            f"Le contenu du fichier ne correspond pas à son extension ({extension}) : il n'est pas accepté."
        )
    return EntNewDocument(name, _TYPES[extension], content)


class BllDocument:
    def __init__(self, dal: DalDocument | None = None) -> None:
        self._dal = dal or DalDocument()

    def upload(self, actor: EntActor, module_id: UUID, file_name: str, content: bytes) -> EntDocument:
        self._require_admin(actor)
        new = check_file(file_name, content)
        if not self._dal.module_exists(module_id):
            raise RecordNotFoundError("Ce module n'existe pas.")
        with acting_as(audit_actor(actor)):
            return self._dal.add(module_id, new, actor.user_id)

    def replace(self, actor: EntActor, document_id: UUID, file_name: str, content: bytes) -> EntDocument:
        self._require_admin(actor)
        old = self._dal.get(document_id)
        if not old.is_current:
            raise InvalidInputError("Ce document a déjà été remplacé : remplacez sa version en vigueur.")
        new = check_file(file_name, content)
        with acting_as(audit_actor(actor)):
            return self._dal.add(old.module_id, new, actor.user_id, replaces=old.id)

    def list_for_training(self, actor: EntActor, training_id: UUID) -> list[EntDocument]:
        """Tous voient les documents en vigueur ; l'administrateur voit aussi
        les versions remplacées."""
        if not actor.roles & CATALOGUE_READERS:
            raise ForbiddenError("Votre rôle ne permet pas de voir le catalogue.")
        documents = self._dal.list_for_training(training_id)
        if Role.IT_ADMIN in actor.roles:
            return documents
        return [d for d in documents if d.is_current]

    def list_all(self, actor: EntActor) -> list[EntDocument]:
        self._require_admin(actor)
        return self._dal.list_all()

    def open(self, actor: EntActor, document_id: UUID) -> tuple[EntDocument, Path]:
        document = self._dal.get(document_id)
        if not self.can_open(actor, document):
            raise ForbiddenError("Seuls le formateur du module et l'administrateur informatique ouvrent ce document.")
        path = self._dal.path(document)
        if not path.exists():
            # Sur le serveur de test, les fichiers se perdent au redémarrage (Q8).
            raise RecordNotFoundError("Le fichier de ce document est introuvable sur le serveur.")
        return document, path

    @staticmethod
    def can_open(actor: EntActor, document: EntDocument) -> bool:
        if Role.IT_ADMIN in actor.roles:
            return True
        return (
            document.is_current
            and Role.TRAINER in actor.roles
            and document.trainer_id is not None
            and document.trainer_id == actor.user_id
        )

    @staticmethod
    def _require_admin(actor: EntActor) -> None:
        if Role.IT_ADMIN not in actor.roles:
            raise ForbiddenError("Seul l'administrateur informatique dépose et remplace les documents de cours.")
