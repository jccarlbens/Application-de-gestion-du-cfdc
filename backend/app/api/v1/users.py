from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.v1.dto.dto_user import UserCreateRequest, UserResponse, UserRolesRequest
from app.api.v1.security import get_current_actor
from app.bll.bll_user import AccountInput, BllUser
from app.entities.ent_user import EntActor

# Les droits de chaque action sont vérifiés par la BLL, avec l'acteur connecté
# (AGENTS.md : « le serveur décide des droits »).
router = APIRouter(prefix="/users", tags=["users"])


def get_bll_user() -> BllUser:
    return BllUser()


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    body: UserCreateRequest,
    actor: EntActor = Depends(get_current_actor),
    bll: BllUser = Depends(get_bll_user),
) -> UserResponse:
    account = AccountInput(body.badge, body.first_name, body.last_name, body.email, body.phone, body.roles)
    return UserResponse.from_entity(bll.create_user(actor, account))


@router.get("", response_model=list[UserResponse])
def list_users(
    actor: EntActor = Depends(get_current_actor),
    bll: BllUser = Depends(get_bll_user),
) -> list[UserResponse]:
    return [UserResponse.from_entity(u) for u in bll.list_users(actor)]


@router.put("/{user_id}/roles", response_model=UserResponse)
def set_roles(
    user_id: UUID,
    body: UserRolesRequest,
    actor: EntActor = Depends(get_current_actor),
    bll: BllUser = Depends(get_bll_user),
) -> UserResponse:
    return UserResponse.from_entity(bll.set_roles(actor, user_id, body.roles))


@router.post("/{user_id}/deactivate", response_model=UserResponse)
def deactivate(
    user_id: UUID,
    actor: EntActor = Depends(get_current_actor),
    bll: BllUser = Depends(get_bll_user),
) -> UserResponse:
    return UserResponse.from_entity(bll.set_active(actor, user_id, is_active=False))


@router.post("/{user_id}/reactivate", response_model=UserResponse)
def reactivate(
    user_id: UUID,
    actor: EntActor = Depends(get_current_actor),
    bll: BllUser = Depends(get_bll_user),
) -> UserResponse:
    return UserResponse.from_entity(bll.set_active(actor, user_id, is_active=True))
