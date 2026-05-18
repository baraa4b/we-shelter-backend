from typing import Any

from beanie import PydanticObjectId

from db.adoption import AdoptionRequest, AdoptionUpdate
from schemas.adoption import AdoptionCreate, AdoptionDecision, AdoptionStatus, AdoptionUpdateCreate
from services import animal_service, image_service
from utils.errors import Conflict, Forbidden, NotFound
from utils.pagination import paginate
from utils.time import utc_now


async def create_request(
    user_id: PydanticObjectId,
    payload: AdoptionCreate,
) -> AdoptionRequest:
    animal = await animal_service.get_animal(payload.animal_id)
    if animal.status != "available":
        raise Conflict("animal is not available for adoption")

    request = AdoptionRequest(
        animal_id=payload.animal_id,
        user_id=user_id,
        message=payload.message,
    )
    await request.insert()

    await animal_service.set_status(payload.animal_id, "pending")
    return request


async def list_for_user(
    user_id: PydanticObjectId,
    page: int,
    page_size: int,
    status: AdoptionStatus | None = None,
) -> dict[str, Any]:
    query: dict[str, Any] = {"user_id": user_id}
    if status is not None:
        query["status"] = status
    cursor = AdoptionRequest.find(query).sort(-AdoptionRequest.created_at)
    return await paginate(cursor, page, page_size)


async def list_for_admin(
    page: int,
    page_size: int,
    status: AdoptionStatus | None = None,
) -> dict[str, Any]:
    query: dict[str, Any] = {}
    if status is not None:
        query["status"] = status
    cursor = AdoptionRequest.find(query).sort(-AdoptionRequest.created_at)
    return await paginate(cursor, page, page_size)


async def get_for_user(
    user_id: PydanticObjectId,
    request_id: PydanticObjectId,
) -> AdoptionRequest:
    request = await AdoptionRequest.get(request_id)
    if request is None or request.user_id != user_id:
        raise NotFound("adoption request not found")
    return request


async def get_for_admin(request_id: PydanticObjectId) -> AdoptionRequest:
    request = await AdoptionRequest.get(request_id)
    if request is None:
        raise NotFound("adoption request not found")
    return request


async def decide(
    request_id: PydanticObjectId,
    admin_id: PydanticObjectId,
    decision: AdoptionDecision,
) -> AdoptionRequest:
    request = await get_for_admin(request_id)
    if request.status != "pending":
        raise Conflict("adoption request is not pending")

    now = utc_now()
    request.status = decision
    request.decided_by_id = admin_id
    request.decided_at = now
    request.updated_at = now
    await request.save()

    new_animal_status = "adopted" if decision == "approved" else "available"
    await animal_service.set_status(request.animal_id, new_animal_status)
    return request


async def add_update(
    user_id: PydanticObjectId,
    request_id: PydanticObjectId,
    payload: AdoptionUpdateCreate,
) -> AdoptionRequest:
    request = await get_for_user(user_id, request_id)
    if request.status != "approved":
        raise Forbidden("updates only allowed after approval")

    request.updates.append(
        AdoptionUpdate(text=payload.text, photo_url=payload.photo_url)
    )
    request.updated_at = utc_now()
    await request.save()
    return request


async def upload_update_photo(
    user_id: PydanticObjectId,
    request_id: PydanticObjectId,
    content_type: str,
    data: bytes,
) -> tuple[PydanticObjectId, str]:
    request = await get_for_user(user_id, request_id)
    if request.status != "approved":
        raise Forbidden("updates only allowed after approval")

    image = await image_service.store(request.animal_id, content_type, data)
    assert image.id is not None
    return image.id, image_service.image_url(image.id)
