from beanie import PydanticObjectId
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from db.user import User
from utils.errors import Forbidden, Unauthorized
from utils.security import decode_token


_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise Unauthorized("missing bearer token")

    user_id = decode_token(credentials.credentials, expected_type="access")
    try:
        object_id = PydanticObjectId(user_id)
    except Exception as exc:
        raise Unauthorized("invalid token subject") from exc

    user = await User.get(object_id)
    if user is None:
        raise Unauthorized("user not found")
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise Forbidden("admin required")
    return user
