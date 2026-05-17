from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from utils.time import utc_now


class AnimalImage(Document):
    animal_id: PydanticObjectId
    content_type: str
    data: bytes
    uploaded_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "animal_images"
        indexes = [
            IndexModel([("animal_id", ASCENDING)], name="images_animal_id"),
        ]
