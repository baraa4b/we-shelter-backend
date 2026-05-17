from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query, status

from db.user import User
from schemas.animal import AnimalRead
from schemas.common import Paginated
from schemas.favorite import FavoriteCreate, FavoriteRead
from services import favorite_service
from utils.deps import get_current_user


router = APIRouter(tags=["user-favorites"])


@router.get("/me/favorites", response_model=Paginated[AnimalRead])
async def list_favorites(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
) -> Paginated[AnimalRead]:
    result = await favorite_service.list_for_user(user.id, page, page_size)
    return Paginated[AnimalRead](
        items=[AnimalRead.model_validate(a) for a in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.post("/me/favorites", response_model=FavoriteRead, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    payload: FavoriteCreate,
    user: User = Depends(get_current_user),
) -> FavoriteRead:
    favorite = await favorite_service.add(user.id, payload.animal_id)
    return FavoriteRead.model_validate(favorite)


@router.delete("/me/favorites/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    animal_id: PydanticObjectId,
    user: User = Depends(get_current_user),
) -> None:
    await favorite_service.remove(user.id, animal_id)
