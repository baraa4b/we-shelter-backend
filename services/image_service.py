from beanie import PydanticObjectId

from db.image import AnimalImage
from utils.errors import BadRequest


ALLOWED_CONTENT_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
MAX_IMAGE_BYTES = 1024 * 1024  # 1 MB


def image_url(image_id: PydanticObjectId) -> str:
    return f"/images/{image_id}"


async def store(
    animal_id: PydanticObjectId,
    content_type: str,
    data: bytes,
) -> AnimalImage:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise BadRequest(f"unsupported content type: {content_type}")
    if not data:
        raise BadRequest("empty image upload")
    if len(data) > MAX_IMAGE_BYTES:
        raise BadRequest("image exceeds 1 MB limit")

    image = AnimalImage(animal_id=animal_id, content_type=content_type, data=data)
    await image.insert()
    return image


async def get_by_id(image_id: PydanticObjectId) -> AnimalImage | None:
    return await AnimalImage.get(image_id)


async def delete_by_id(image_id: PydanticObjectId) -> None:
    image = await AnimalImage.get(image_id)
    if image is not None:
        await image.delete()


async def delete_all_for_animal(animal_id: PydanticObjectId) -> None:
    await AnimalImage.find(AnimalImage.animal_id == animal_id).delete()
