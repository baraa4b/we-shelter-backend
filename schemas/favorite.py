from datetime import datetime

from beanie import PydanticObjectId

from schemas.common import BaseSchema


class FavoriteRead(BaseSchema):
    id: PydanticObjectId
    user_id: PydanticObjectId
    animal_id: PydanticObjectId
    created_at: datetime


class FavoriteCreate(BaseSchema):
    animal_id: PydanticObjectId
