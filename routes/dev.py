"""Dev-only utility routes.

Gated by a static X-Dev-Key header (see utils.deps.require_dev_key). These exist
so the local `helpers/` scripts can promote admins, create users, and bulk-load
data without going through the full UI. Leave DEV_KEY unset in production and the
whole router returns 404.
"""

from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic import EmailStr, Field

from db.animal import Animal
from db.user import User
from schemas.animal import AnimalCreate, AnimalRead
from schemas.common import BaseSchema
from schemas.user import Role, UserRead
from scripts.seed import (
    _seed_adoptions,
    _seed_animals,
    _seed_notes,
    _seed_users,
)
from utils.deps import require_dev_key
from utils.errors import Conflict, NotFound
from utils.security import hash_password
from utils.time import utc_now


router = APIRouter(
    prefix="/dev",
    tags=["dev"],
    dependencies=[Depends(require_dev_key)],
)


class GrantAdminRequest(BaseSchema):
    email: EmailStr


class CreateUserRequest(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=100)
    role: Role = "user"


class BulkAnimalsRequest(BaseSchema):
    animals: list[AnimalCreate]


class MessageResponse(BaseSchema):
    ok: bool = True
    message: str


@router.get("/ping", response_model=MessageResponse)
async def ping() -> MessageResponse:
    return MessageResponse(message="dev key accepted")


@router.get("/users", response_model=list[UserRead])
async def list_all_users() -> list[UserRead]:
    users = await User.find_all().sort(-User.created_at).to_list()
    return [UserRead.model_validate(u) for u in users]


@router.post("/grant-admin", response_model=UserRead)
async def grant_admin(payload: GrantAdminRequest) -> UserRead:
    user = await User.find_one(User.email == payload.email.lower())
    if user is None:
        raise NotFound("user not found")
    user.role = "admin"
    user.updated_at = utc_now()
    await user.save()
    return UserRead.model_validate(user)


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: CreateUserRequest) -> UserRead:
    email = payload.email.lower()
    if await User.find_one(User.email == email) is not None:
        raise Conflict("email already registered")
    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    await user.insert()
    return UserRead.model_validate(user)


@router.post(
    "/animals/bulk",
    response_model=list[AnimalRead],
    status_code=status.HTTP_201_CREATED,
)
async def bulk_create_animals(payload: BulkAnimalsRequest) -> list[AnimalRead]:
    created: list[AnimalRead] = []
    for entry in payload.animals:
        animal = Animal(**entry.model_dump())
        await animal.insert()
        created.append(AnimalRead.model_validate(animal))
    return created


@router.post("/seed", response_model=MessageResponse)
async def run_seed() -> MessageResponse:
    """Run the same routine as `python -m scripts.seed`, minus the DB lifecycle
    (the API process already has Beanie initialized)."""
    admin, user = await _seed_users()
    animals = await _seed_animals()
    await _seed_notes(animals, admin)
    await _seed_adoptions(animals, admin, user)
    summary: dict[str, Any] = {
        "animals": len(animals),
        "admin": admin.email,
        "user": user.email,
    }
    return MessageResponse(message=f"seed complete: {summary}")
