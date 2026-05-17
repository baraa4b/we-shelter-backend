from datetime import datetime
from typing import Literal

from beanie import Document
from pydantic import EmailStr, Field
from pymongo import ASCENDING, IndexModel

from utils.time import utc_now


class User(Document):
    email: EmailStr
    password_hash: str
    full_name: str
    role: Literal["user", "admin"] = "user"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "users"
        indexes = [
            IndexModel([("email", ASCENDING)], unique=True, name="users_email_unique"),
        ]
