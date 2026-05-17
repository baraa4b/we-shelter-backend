from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from utils.time import utc_now


class Favorite(Document):
    user_id: PydanticObjectId
    animal_id: PydanticObjectId
    created_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "favorites"
        indexes = [
            IndexModel(
                [("user_id", ASCENDING), ("animal_id", ASCENDING)],
                unique=True,
                name="favorites_user_animal_unique",
            ),
        ]
