from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from config import get_settings
from db.adoption import AdoptionRequest
from db.animal import Animal
from db.favorite import Favorite
from db.image import AnimalImage
from db.note import AnimalNote
from db.user import User


_DOCUMENT_MODELS = [User, Animal, AdoptionRequest, AnimalNote, AnimalImage, Favorite]

_client: AsyncIOMotorClient | None = None


async def init_db() -> None:
    global _client
    settings = get_settings()
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    database = _client[settings.mongodb_db]
    await init_beanie(database=database, document_models=_DOCUMENT_MODELS)


async def close_db() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
