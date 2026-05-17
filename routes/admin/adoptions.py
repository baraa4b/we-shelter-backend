from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query

from db.user import User
from schemas.adoption import (
    AdoptionDecisionRequest,
    AdoptionRead,
    AdoptionStatus,
)
from schemas.common import Paginated
from services import adoption_service
from utils.deps import require_admin


router = APIRouter(
    prefix="/admin/adoptions",
    tags=["admin-adoptions"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=Paginated[AdoptionRead])
async def list_adoptions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    status_filter: AdoptionStatus | None = Query(default=None, alias="status"),
) -> Paginated[AdoptionRead]:
    result = await adoption_service.list_for_admin(page, page_size, status_filter)
    return Paginated[AdoptionRead](
        items=[AdoptionRead.model_validate(r) for r in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.get("/{request_id}", response_model=AdoptionRead)
async def get_adoption(request_id: PydanticObjectId) -> AdoptionRead:
    request = await adoption_service.get_for_admin(request_id)
    return AdoptionRead.model_validate(request)


@router.patch("/{request_id}", response_model=AdoptionRead)
async def decide_adoption(
    request_id: PydanticObjectId,
    payload: AdoptionDecisionRequest,
    admin: User = Depends(require_admin),
) -> AdoptionRead:
    request = await adoption_service.decide(request_id, admin.id, payload.status)
    return AdoptionRead.model_validate(request)
