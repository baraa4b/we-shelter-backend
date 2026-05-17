from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, File, UploadFile, status

from schemas.animal import (
    AnimalCreate,
    AnimalPatch,
    AnimalRead,
    AnimalReplace,
    ImageUploaded,
)
from services import animal_service
from utils.deps import require_admin


router = APIRouter(
    prefix="/admin/animals",
    tags=["admin-animals"],
    dependencies=[Depends(require_admin)],
)


@router.post("", response_model=AnimalRead, status_code=status.HTTP_201_CREATED)
async def create_animal(payload: AnimalCreate) -> AnimalRead:
    animal = await animal_service.create_animal(payload)
    return AnimalRead.model_validate(animal)


@router.put("/{animal_id}", response_model=AnimalRead)
async def replace_animal(
    animal_id: PydanticObjectId,
    payload: AnimalReplace,
) -> AnimalRead:
    animal = await animal_service.replace_animal(animal_id, payload)
    return AnimalRead.model_validate(animal)


@router.patch("/{animal_id}", response_model=AnimalRead)
async def patch_animal(
    animal_id: PydanticObjectId,
    payload: AnimalPatch,
) -> AnimalRead:
    animal = await animal_service.patch_animal(animal_id, payload)
    return AnimalRead.model_validate(animal)


@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_animal(animal_id: PydanticObjectId) -> None:
    await animal_service.delete_animal(animal_id)


@router.post(
    "/{animal_id}/images",
    response_model=ImageUploaded,
    status_code=status.HTTP_201_CREATED,
)
async def upload_image(
    animal_id: PydanticObjectId,
    file: UploadFile = File(...),
) -> ImageUploaded:
    data = await file.read()
    return await animal_service.upload_photo(
        animal_id=animal_id,
        content_type=file.content_type or "application/octet-stream",
        data=data,
    )


@router.delete(
    "/{animal_id}/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_image(
    animal_id: PydanticObjectId,
    image_id: PydanticObjectId,
) -> None:
    await animal_service.delete_photo(animal_id, image_id)
