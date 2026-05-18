from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from db.user import User
from schemas.adoption import (
    AdoptionCreate,
    AdoptionRead,
    AdoptionStatus,
    AdoptionUpdateCreate,
)
from schemas.animal import ImageUploaded
from schemas.common import Paginated
from services import adoption_service
from utils.deps import get_current_user


router = APIRouter(tags=["user-adoptions"])


@router.post("/adoptions", response_model=AdoptionRead, status_code=status.HTTP_201_CREATED)
async def create_adoption(
    payload: AdoptionCreate,
    user: User = Depends(get_current_user),
) -> AdoptionRead:
    request = await adoption_service.create_request(user.id, payload)
    return AdoptionRead.model_validate(request)


@router.get("/me/adoptions", response_model=Paginated[AdoptionRead])
async def list_my_adoptions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    status_filter: AdoptionStatus | None = Query(default=None, alias="status"),
    user: User = Depends(get_current_user),
) -> Paginated[AdoptionRead]:
    result = await adoption_service.list_for_user(user.id, page, page_size, status_filter)
    return Paginated[AdoptionRead](
        items=[AdoptionRead.model_validate(r) for r in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.get("/me/adoptions/{request_id}", response_model=AdoptionRead)
async def get_my_adoption(
    request_id: PydanticObjectId,
    user: User = Depends(get_current_user),
) -> AdoptionRead:
    request = await adoption_service.get_for_user(user.id, request_id)
    return AdoptionRead.model_validate(request)


@router.post(
    "/me/adoptions/{request_id}/updates",
    response_model=AdoptionRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_adoption_update(
    request_id: PydanticObjectId,
    payload: AdoptionUpdateCreate,
    user: User = Depends(get_current_user),
) -> AdoptionRead:
    request = await adoption_service.add_update(user.id, request_id, payload)
    return AdoptionRead.model_validate(request)


@router.post(
    "/me/adoptions/{request_id}/images",
    response_model=ImageUploaded,
    status_code=status.HTTP_201_CREATED,
)
async def upload_adoption_image(
    request_id: PydanticObjectId,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
) -> ImageUploaded:
    data = await file.read()
    image_id, url = await adoption_service.upload_update_photo(
        user_id=user.id,
        request_id=request_id,
        content_type=file.content_type or "application/octet-stream",
        data=data,
    )
    return ImageUploaded(image_id=image_id, url=url)
