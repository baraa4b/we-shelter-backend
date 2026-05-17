from pydantic import EmailStr, Field

from schemas.common import BaseSchema
from schemas.user import UserRead


class RegisterRequest(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=100)


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str


class RefreshRequest(BaseSchema):
    refresh_token: str


class TokenPair(BaseSchema):
    user: UserRead
    access_token: str
    refresh_token: str


class AccessTokenResponse(BaseSchema):
    access_token: str
