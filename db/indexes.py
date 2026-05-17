from beanie import Document

from db.adoption import AdoptionRequest
from db.animal import Animal
from db.favorite import Favorite
from db.image import AnimalImage
from db.note import AnimalNote
from db.user import User


_MODELS: tuple[type[Document], ...] = (
    User,
    Animal,
    AdoptionRequest,
    AnimalNote,
    AnimalImage,
    Favorite,
)


async def ensure_indexes() -> None:
    # Beanie also creates indexes during init_beanie, but calling this explicitly
    # keeps index creation deterministic and safe to re-run after schema edits.
    for model in _MODELS:
        index_models = getattr(model.Settings, "indexes", None)
        if not index_models:
            continue
        collection = model.get_motor_collection()
        await collection.create_indexes(index_models)
