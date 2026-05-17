from typing import Any

from beanie import PydanticObjectId

from db.user import User
from schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    RegisterRequest,
    TokenPair,
)
from schemas.user import Role, UserRead
from utils.errors import Conflict, NotFound, Unauthorized
from utils.pagination import paginate
from utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from utils.time import utc_now


async def register(payload: RegisterRequest) -> TokenPair:
    email = payload.email.lower()
    if await User.find_one(User.email == email) is not None:
        raise Conflict("email already registered")

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
    )
    await user.insert()
    return _issue_tokens(user)


async def login(payload: LoginRequest) -> TokenPair:
    email = payload.email.lower()
    user = await User.find_one(User.email == email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise Unauthorized("invalid credentials")
    return _issue_tokens(user)


async def refresh(refresh_token: str) -> AccessTokenResponse:
    user_id = decode_token(refresh_token, expected_type="refresh")
    # Confirm the user still exists; a refresh token for a deleted user must not
    # mint a new access token.
    if await User.get(PydanticObjectId(user_id)) is None:
        raise Unauthorized("user not found")
    return AccessTokenResponse(access_token=create_access_token(user_id))


async def list_users(
    page: int,
    page_size: int,
    role: Role | None = None,
) -> dict[str, Any]:
    query = User.find(User.role == role) if role is not None else User.find_all()
    query = query.sort(-User.created_at)
    return await paginate(query, page, page_size)


async def update_user_role(user_id: PydanticObjectId, role: Role) -> User:
    user = await User.get(user_id)
    if user is None:
        raise NotFound("user not found")
    user.role = role
    user.updated_at = utc_now()
    await user.save()
    return user


def _issue_tokens(user: User) -> TokenPair:
    user_id = str(user.id)
    return TokenPair(
        user=UserRead.model_validate(user),
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )
