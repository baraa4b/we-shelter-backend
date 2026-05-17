from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query

from schemas.common import Paginated
from schemas.user import Role, UserRead, UserRoleUpdate
from services import auth_service
from utils.deps import require_admin


router = APIRouter(
    prefix="/admin/users",
    tags=["admin-users"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=Paginated[UserRead])
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    role: Role | None = None,
) -> Paginated[UserRead]:
    result = await auth_service.list_users(page, page_size, role)
    return Paginated[UserRead](
        items=[UserRead.model_validate(u) for u in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.patch("/{user_id}/role", response_model=UserRead)
async def update_role(
    user_id: PydanticObjectId,
    payload: UserRoleUpdate,
) -> UserRead:
    user = await auth_service.update_user_role(user_id, payload.role)
    return UserRead.model_validate(user)
