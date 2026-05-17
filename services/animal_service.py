from typing import Any

from beanie import PydanticObjectId

from db.animal import Animal, AnimalStatus
from schemas.animal import (
    AnimalCreate,
    AnimalFilters,
    AnimalPatch,
    AnimalReplace,
    ImageUploaded,
)
from services import favorite_service, image_service, note_service
from utils.errors import BadRequest, NotFound
from utils.pagination import paginate
from utils.time import utc_now


MAX_PHOTOS_PER_ANIMAL = 5


async def list_animals(
    filters: AnimalFilters,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    query: dict[str, Any] = {}

    if filters.species is not None:
        query["species"] = filters.species
    if filters.gender is not None:
        query["gender"] = filters.gender
    if filters.status is not None:
        query["status"] = filters.status
    if filters.vaccinated is not None:
        query["vaccinated"] = filters.vaccinated

    age_range: dict[str, float] = {}
    if filters.min_age is not None:
        age_range["$gte"] = filters.min_age
    if filters.max_age is not None:
        age_range["$lte"] = filters.max_age
    if age_range:
        query["age_years"] = age_range

    if filters.q:
        query["$or"] = [
            {"name": {"$regex": filters.q, "$options": "i"}},
            {"breed": {"$regex": filters.q, "$options": "i"}},
            {"description": {"$regex": filters.q, "$options": "i"}},
        ]

    cursor = Animal.find(query).sort(-Animal.created_at)
    return await paginate(cursor, page, page_size)


async def get_animal(animal_id: PydanticObjectId) -> Animal:
    animal = await Animal.get(animal_id)
    if animal is None:
        raise NotFound("animal not found")
    return animal


async def create_animal(payload: AnimalCreate) -> Animal:
    animal = Animal(**payload.model_dump())
    await animal.insert()
    return animal


async def replace_animal(animal_id: PydanticObjectId, payload: AnimalReplace) -> Animal:
    animal = await get_animal(animal_id)
    for field, value in payload.model_dump().items():
        setattr(animal, field, value)
    animal.updated_at = utc_now()
    await animal.save()
    return animal


async def patch_animal(animal_id: PydanticObjectId, payload: AnimalPatch) -> Animal:
    animal = await get_animal(animal_id)
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(animal, field, value)
    animal.updated_at = utc_now()
    await animal.save()
    return animal


async def delete_animal(animal_id: PydanticObjectId) -> None:
    animal = await get_animal(animal_id)
    await image_service.delete_all_for_animal(animal_id)
    await note_service.delete_all_for_animal(animal_id)
    await favorite_service.delete_all_for_animal(animal_id)
    await animal.delete()


async def set_status(animal_id: PydanticObjectId, status: AnimalStatus) -> Animal:
    animal = await get_animal(animal_id)
    animal.status = status
    animal.updated_at = utc_now()
    await animal.save()
    return animal


async def upload_photo(
    animal_id: PydanticObjectId,
    content_type: str,
    data: bytes,
) -> ImageUploaded:
    animal = await get_animal(animal_id)
    if len(animal.photos) >= MAX_PHOTOS_PER_ANIMAL:
        raise BadRequest(f"max {MAX_PHOTOS_PER_ANIMAL} photos per animal")

    image = await image_service.store(animal_id, content_type, data)
    assert image.id is not None
    url = image_service.image_url(image.id)
    animal.photos.append(url)
    animal.updated_at = utc_now()
    await animal.save()
    return ImageUploaded(image_id=image.id, url=url)


async def delete_photo(
    animal_id: PydanticObjectId,
    image_id: PydanticObjectId,
) -> None:
    animal = await get_animal(animal_id)
    image = await image_service.get_by_id(image_id)
    if image is None or image.animal_id != animal_id:
        raise NotFound("image not found")

    url = image_service.image_url(image_id)
    if url in animal.photos:
        animal.photos.remove(url)
        animal.updated_at = utc_now()
        await animal.save()

    await image_service.delete_by_id(image_id)
