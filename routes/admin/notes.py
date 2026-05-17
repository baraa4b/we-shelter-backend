from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from db.user import User
from schemas.note import NoteCreate, NoteRead
from services import note_service
from utils.deps import require_admin


router = APIRouter(
    prefix="/admin/animals",
    tags=["admin-notes"],
    dependencies=[Depends(require_admin)],
)


@router.post(
    "/{animal_id}/notes",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_note(
    animal_id: PydanticObjectId,
    payload: NoteCreate,
    admin: User = Depends(require_admin),
) -> NoteRead:
    note = await note_service.create(animal_id, admin.id, payload.text)
    return NoteRead.model_validate(note)


@router.delete(
    "/{animal_id}/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_note(animal_id: PydanticObjectId, note_id: PydanticObjectId) -> None:
    await note_service.delete(animal_id, note_id)
