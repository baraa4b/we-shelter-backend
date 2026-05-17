from datetime import datetime
from typing import Literal

from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, TEXT, IndexModel

from utils.time import utc_now


Species = Literal["dog", "cat", "bird", "rabbit", "other"]
Gender = Literal["male", "female"]
AnimalStatus = Literal["available", "pending", "adopted"]


class Animal(Document):
    name: str
    species: Species
    breed: str | None = None
    age_years: float
    gender: Gender
    vaccinated: bool = False
    neutered: bool = False
    status: AnimalStatus = "available"
    description: str
    photos: list[str] = Field(default_factory=list)
    arrived_at: datetime
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "animals"
        indexes = [
            IndexModel(
                [("name", TEXT), ("breed", TEXT), ("description", TEXT)],
                name="animals_text_search",
            ),
            IndexModel(
                [("status", ASCENDING), ("species", ASCENDING)],
                name="animals_status_species",
            ),
        ]
