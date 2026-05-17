from datetime import datetime
from typing import Literal

from beanie import PydanticObjectId
from pydantic import Field

from schemas.common import BaseSchema


AdoptionStatus = Literal["pending", "approved", "rejected", "completed"]
AdoptionDecision = Literal["approved", "rejected"]


class AdoptionUpdateRead(BaseSchema):
    text: str
    photo_url: str | None
    created_at: datetime


class AdoptionRead(BaseSchema):
    id: PydanticObjectId
    animal_id: PydanticObjectId
    user_id: PydanticObjectId
    message: str | None
    status: AdoptionStatus
    decided_by_id: PydanticObjectId | None
    decided_at: datetime | None
    updates: list[AdoptionUpdateRead]
    created_at: datetime
    updated_at: datetime


class AdoptionCreate(BaseSchema):
    animal_id: PydanticObjectId
    message: str | None = Field(default=None, max_length=1000)


class AdoptionDecisionRequest(BaseSchema):
    status: AdoptionDecision


class AdoptionUpdateCreate(BaseSchema):
    text: str = Field(min_length=1, max_length=2000)
    photo_url: str | None = Field(default=None, max_length=500)
