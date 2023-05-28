import uuid
from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None = None
    created_at: datetime


class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str


class UserRoleResponse(BaseModel):
    id: uuid.UUID
    name: str
