from beanie import PydanticObjectId
from fastapi import APIRouter, Query

from schemas.animal import AnimalFilters, AnimalRead, AnimalStatus, Gender, Species
from schemas.common import Paginated
from schemas.note import NoteRead
from services import animal_service, note_service


router = APIRouter(tags=["animals"])


@router.get("/animals", response_model=Paginated[AnimalRead])
async def list_animals(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    species: Species | None = None,
    gender: Gender | None = None,
    status: AnimalStatus | None = None,
    min_age: float | None = Query(default=None, ge=0, alias="minAge"),
    max_age: float | None = Query(default=None, ge=0, alias="maxAge"),
    vaccinated: bool | None = None,
    q: str | None = None,
) -> Paginated[AnimalRead]:
    filters = AnimalFilters(
        species=species,
        gender=gender,
        status=status,
        min_age=min_age,
        max_age=max_age,
        vaccinated=vaccinated,
        q=q,
    )
    result = await animal_service.list_animals(filters, page, page_size)
    return Paginated[AnimalRead](
        items=[AnimalRead.model_validate(a) for a in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.get("/animals/{animal_id}", response_model=AnimalRead)
async def get_animal(animal_id: PydanticObjectId) -> AnimalRead:
    animal = await animal_service.get_animal(animal_id)
    return AnimalRead.model_validate(animal)


@router.get("/animals/{animal_id}/notes", response_model=list[NoteRead])
async def list_animal_notes(animal_id: PydanticObjectId) -> list[NoteRead]:
    notes = await note_service.list_for_animal(animal_id)
    return [NoteRead.model_validate(n) for n in notes]
