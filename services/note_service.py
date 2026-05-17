from beanie import PydanticObjectId

from db.note import AnimalNote
from utils.errors import NotFound


async def list_for_animal(animal_id: PydanticObjectId) -> list[AnimalNote]:
    return (
        await AnimalNote.find(AnimalNote.animal_id == animal_id)
        .sort(-AnimalNote.created_at)
        .to_list()
    )


async def create(
    animal_id: PydanticObjectId,
    author_id: PydanticObjectId,
    text: str,
) -> AnimalNote:
    note = AnimalNote(animal_id=animal_id, author_id=author_id, text=text)
    await note.insert()
    return note


async def delete(animal_id: PydanticObjectId, note_id: PydanticObjectId) -> None:
    note = await AnimalNote.get(note_id)
    if note is None or note.animal_id != animal_id:
        raise NotFound("note not found")
    await note.delete()


async def delete_all_for_animal(animal_id: PydanticObjectId) -> None:
    await AnimalNote.find(AnimalNote.animal_id == animal_id).delete()
