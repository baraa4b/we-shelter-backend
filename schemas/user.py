from datetime import datetime
from typing import Literal

from beanie import PydanticObjectId
from pydantic import EmailStr

from schemas.common import BaseSchema


Role = Literal["user", "admin"]


class UserRead(BaseSchema):
    id: PydanticObjectId
    email: EmailStr
    full_name: str
    role: Role
    created_at: datetime
    updated_at: datetime


class UserRoleUpdate(BaseSchema):
    role: Role
