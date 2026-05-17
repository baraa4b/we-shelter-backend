from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from utils.time import utc_now


class AnimalNote(Document):
    animal_id: PydanticObjectId
    text: str
    author_id: PydanticObjectId
    created_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "animal_notes"
        indexes = [
            IndexModel([("animal_id", ASCENDING)], name="notes_animal_id"),
        ]
