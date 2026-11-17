from pydantic import BaseModel, Field

from app.entities.ent_user import EntUser


class LoginRequest(BaseModel):
    badge: str = Field(max_length=20)
    password: str = Field(max_length=200)


class MeResponse(BaseModel):
    badge: str
    first_name: str
    last_name: str
    roles: list[str]

    @classmethod
    def from_entity(cls, user: EntUser) -> "MeResponse":
        return cls(
            badge=user.badge,
            first_name=user.first_name,
            last_name=user.last_name,
            roles=sorted(role.value for role in user.roles),
        )
