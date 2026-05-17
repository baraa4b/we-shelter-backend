from beanie import PydanticObjectId
from fastapi import APIRouter, Response

from services import image_service
from utils.errors import NotFound


router = APIRouter(tags=["images"])


@router.get("/images/{image_id}")
async def get_image(image_id: PydanticObjectId) -> Response:
    image = await image_service.get_by_id(image_id)
    if image is None:
        raise NotFound("image not found")
    return Response(content=image.data, media_type=image.content_type)
