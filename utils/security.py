from datetime import UTC, datetime, timedelta
from typing import Literal

import bcrypt
import jwt

from config import get_settings
from utils.errors import Unauthorized


TokenType = Literal["access", "refresh"]

_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def _encode(user_id: str, token_type: TokenType, expires_in: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "typ": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_in).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=_ALGORITHM)


def create_access_token(user_id: str) -> str:
    settings = get_settings()
    return _encode(user_id, "access", timedelta(minutes=settings.jwt_access_ttl_min))


def create_refresh_token(user_id: str) -> str:
    settings = get_settings()
    return _encode(user_id, "refresh", timedelta(days=settings.jwt_refresh_ttl_days))


def decode_token(token: str, expected_type: TokenType) -> str:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise Unauthorized("token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise Unauthorized("invalid token") from exc

    if payload.get("typ") != expected_type:
        raise Unauthorized("wrong token type")

    user_id = payload.get("sub")
    if not isinstance(user_id, str) or not user_id:
        raise Unauthorized("invalid token subject")
    return user_id
