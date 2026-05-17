from datetime import datetime
from typing import Literal

from beanie import PydanticObjectId
from pydantic import Field

from schemas.common import BaseSchema


Species = Literal["dog", "cat", "bird", "rabbit", "other"]
Gender = Literal["male", "female"]
AnimalStatus = Literal["available", "pending", "adopted"]


class AnimalRead(BaseSchema):
    id: PydanticObjectId
    name: str
    species: Species
    breed: str | None
    age_years: float
    gender: Gender
    vaccinated: bool
    neutered: bool
    status: AnimalStatus
    description: str
    photos: list[str]
    arrived_at: datetime
    created_at: datetime
    updated_at: datetime


class AnimalCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=80)
    species: Species
    breed: str | None = Field(default=None, max_length=80)
    age_years: float = Field(ge=0, le=50)
    gender: Gender
    vaccinated: bool = False
    neutered: bool = False
    status: AnimalStatus = "available"
    description: str = Field(min_length=1, max_length=2000)
    arrived_at: datetime


class AnimalReplace(BaseSchema):
    name: str = Field(min_length=1, max_length=80)
    species: Species
    breed: str | None = Field(default=None, max_length=80)
    age_years: float = Field(ge=0, le=50)
    gender: Gender
    vaccinated: bool
    neutered: bool
    status: AnimalStatus
    description: str = Field(min_length=1, max_length=2000)
    arrived_at: datetime


class AnimalPatch(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    species: Species | None = None
    breed: str | None = Field(default=None, max_length=80)
    age_years: float | None = Field(default=None, ge=0, le=50)
    gender: Gender | None = None
    vaccinated: bool | None = None
    neutered: bool | None = None
    status: AnimalStatus | None = None
    description: str | None = Field(default=None, min_length=1, max_length=2000)
    arrived_at: datetime | None = None


class AnimalFilters(BaseSchema):
    species: Species | None = None
    gender: Gender | None = None
    status: AnimalStatus | None = None
    min_age: float | None = None
    max_age: float | None = None
    vaccinated: bool | None = None
    q: str | None = None


class ImageUploaded(BaseSchema):
    image_id: PydanticObjectId
    url: str
