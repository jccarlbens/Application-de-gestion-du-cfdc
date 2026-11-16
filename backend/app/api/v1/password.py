from fastapi import APIRouter, Depends, Response

from app.api.v1.dto.dto_user import PasswordSetupRequest
from app.api.v1.users import get_bll_user
from app.bll.bll_user import BllUser

router = APIRouter(prefix="/password", tags=["password"])


@router.post("/setup", status_code=204)
def set_password_with_link(body: PasswordSetupRequest, bll: BllUser = Depends(get_bll_user)) -> Response:
    """Sans connexion : le lien reçu par email tient lieu de preuve (US-002)."""
    bll.set_password_with_link(body.token, body.password)
    return Response(status_code=204)
