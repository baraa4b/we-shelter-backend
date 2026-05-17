from typing import Any

from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from db.animal import Animal
from db.favorite import Favorite
from utils.errors import NotFound
from utils.pagination import clamp_page, clamp_page_size


async def list_for_user(
    user_id: PydanticObjectId,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    page = clamp_page(page)
    page_size = clamp_page_size(page_size)

    base = Favorite.find(Favorite.user_id == user_id).sort(-Favorite.created_at)
    total = await base.count()
    favorites = await base.skip((page - 1) * page_size).limit(page_size).to_list()

    animal_ids = [f.animal_id for f in favorites]
    animals = await Animal.find({"_id": {"$in": animal_ids}}).to_list() if animal_ids else []
    by_id = {animal.id: animal for animal in animals}
    items = [by_id[f.animal_id] for f in favorites if f.animal_id in by_id]

    return {"items": items, "total": total, "page": page, "page_size": page_size}


async def add(user_id: PydanticObjectId, animal_id: PydanticObjectId) -> Favorite:
    if await Animal.get(animal_id) is None:
        raise NotFound("animal not found")

    existing = await Favorite.find_one(
        Favorite.user_id == user_id,
        Favorite.animal_id == animal_id,
    )
    if existing is not None:
        return existing

    favorite = Favorite(user_id=user_id, animal_id=animal_id)
    try:
        await favorite.insert()
    except DuplicateKeyError:
        # Concurrent insert won the race — return whatever ended up in storage.
        winner = await Favorite.find_one(
            Favorite.user_id == user_id,
            Favorite.animal_id == animal_id,
        )
        if winner is None:
            raise
        return winner
    return favorite


async def remove(user_id: PydanticObjectId, animal_id: PydanticObjectId) -> None:
    favorite = await Favorite.find_one(
        Favorite.user_id == user_id,
        Favorite.animal_id == animal_id,
    )
    if favorite is not None:
        await favorite.delete()


async def delete_all_for_animal(animal_id: PydanticObjectId) -> None:
    await Favorite.find(Favorite.animal_id == animal_id).delete()
