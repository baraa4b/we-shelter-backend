from datetime import datetime
from typing import Literal

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from pymongo import ASCENDING, IndexModel

from utils.time import utc_now


AdoptionStatus = Literal["pending", "approved", "rejected", "completed"]


class AdoptionUpdate(BaseModel):
    text: str
    photo_url: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class AdoptionRequest(Document):
    animal_id: PydanticObjectId
    user_id: PydanticObjectId
    message: str | None = None
    status: AdoptionStatus = "pending"
    decided_by_id: PydanticObjectId | None = None
    decided_at: datetime | None = None
    updates: list[AdoptionUpdate] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "adoption_requests"
        indexes = [
            IndexModel(
                [("user_id", ASCENDING), ("status", ASCENDING)],
                name="adoptions_user_status",
            ),
            IndexModel(
                [("status", ASCENDING), ("created_at", ASCENDING)],
                name="adoptions_status_created",
            ),
        ]
