from datetime import datetime

from beanie import PydanticObjectId
from pydantic import Field

from schemas.common import BaseSchema


class NoteRead(BaseSchema):
    id: PydanticObjectId
    animal_id: PydanticObjectId
    text: str
    author_id: PydanticObjectId
    created_at: datetime


class NoteCreate(BaseSchema):
    text: str = Field(min_length=1, max_length=2000)
