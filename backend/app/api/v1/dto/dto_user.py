from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.entities.ent_user import EntUser


class UserCreateRequest(BaseModel):
    badge: str = Field(max_length=20)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: str = Field(max_length=254)
    phone: str | None = Field(default=None, max_length=30)
    roles: list[str]


class UserRolesRequest(BaseModel):
    roles: list[str]


class UserResponse(BaseModel):
    id: UUID
    badge: str
    first_name: str
    last_name: str
    email: str
    phone: str | None
    roles: list[str]
    is_active: bool
    is_blocked: bool
    has_password: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, user: EntUser) -> "UserResponse":
        return cls(
            id=user.id,
            badge=user.badge,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            roles=sorted(role.value for role in user.roles),
            is_active=user.is_active,
            is_blocked=user.is_blocked,
            has_password=user.has_password,
            created_at=user.created_at,
        )


class PasswordSetupRequest(BaseModel):
    token: str = Field(min_length=1, max_length=200)
    password: str = Field(max_length=200)
