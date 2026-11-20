from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse

from app.api.v1.dto.dto_document import DocumentResponse
from app.api.v1.security import require_roles
from app.bll.bll_document import BllDocument
from app.bll.bll_training import CATALOGUE_READERS
from app.core.config import settings
from app.entities.ent_user import EntActor, Role

# Les documents de cours (US-012). Chaque route déclare ses rôles ; la BLL
# vérifie de nouveau, et décide seule qui ouvre quel document.
READERS = require_roles(*CATALOGUE_READERS)
ADMIN_ONLY = require_roles(Role.IT_ADMIN)
# Ouvrir un document : le formateur du module ou l'administrateur ; la BLL
# vérifie que ce formateur est bien celui du module.
OPENERS = require_roles(Role.TRAINER, Role.IT_ADMIN)

router = APIRouter(tags=["documents"])


def get_bll_document() -> BllDocument:
    return BllDocument()


def _read(upload: UploadFile) -> bytes:
    # Un octet de plus que la limite suffit à savoir qu'elle est dépassée,
    # sans lire en mémoire un fichier démesuré.
    return upload.file.read(settings.document_max_bytes + 1)


@router.get("/documents", response_model=list[DocumentResponse])
def list_documents(actor: EntActor = Depends(ADMIN_ONLY), bll: BllDocument = Depends(get_bll_document)):
    return [DocumentResponse.from_entity(d) for d in bll.list_all(actor)]


@router.get("/trainings/{training_id}/documents", response_model=list[DocumentResponse])
def list_training_documents(
    training_id: UUID, actor: EntActor = Depends(READERS), bll: BllDocument = Depends(get_bll_document)
):
    return [DocumentResponse.from_entity(d) for d in bll.list_for_training(actor, training_id)]


@router.post("/modules/{module_id}/documents", response_model=DocumentResponse, status_code=201)
def upload_document(
    module_id: UUID,
    file: UploadFile = File(...),
    actor: EntActor = Depends(ADMIN_ONLY),
    bll: BllDocument = Depends(get_bll_document),
):
    return DocumentResponse.from_entity(bll.upload(actor, module_id, file.filename or "", _read(file)))


@router.post("/documents/{document_id}/replace", response_model=DocumentResponse, status_code=201)
def replace_document(
    document_id: UUID,
    file: UploadFile = File(...),
    actor: EntActor = Depends(ADMIN_ONLY),
    bll: BllDocument = Depends(get_bll_document),
):
    return DocumentResponse.from_entity(bll.replace(actor, document_id, file.filename or "", _read(file)))


@router.get("/documents/{document_id}/download")
def download_document(
    document_id: UUID, actor: EntActor = Depends(OPENERS), bll: BllDocument = Depends(get_bll_document)
) -> FileResponse:
    document, path = bll.open(actor, document_id)
    # Le nom d'origine, accents compris (Starlette l'encode selon la RFC 5987).
    return FileResponse(path, media_type=document.content_type, filename=document.file_name)
