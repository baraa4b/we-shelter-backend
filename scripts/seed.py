import asyncio
from datetime import timedelta
from typing import Any

from db.adoption import AdoptionRequest
from db.animal import Animal
from db.client import close_db, init_db
from db.note import AnimalNote
from db.user import User
from utils.security import hash_password
from utils.time import utc_now


ADMIN_EMAIL = "admin@shelter.com"
ADMIN_PASSWORD = "Admin123!"
USER_EMAIL = "user@shelter.com"
USER_PASSWORD = "User123!"


ANIMALS: list[dict[str, Any]] = [
    {
        "name": "Luna",
        "species": "dog",
        "breed": "Golden Retriever",
        "age_years": 3,
        "gender": "female",
        "vaccinated": True,
        "neutered": True,
        "description": (
            "Friendly Golden Retriever who adores belly rubs and long park walks. "
            "House-trained and excellent with children."
        ),
        "days_ago": 45,
    },
    {
        "name": "Max",
        "species": "dog",
        "breed": "German Shepherd",
        "age_years": 5,
        "gender": "male",
        "vaccinated": True,
        "neutered": True,
        "description": (
            "Loyal and intelligent German Shepherd who responds well to commands. "
            "Best suited to a calm home with experienced owners."
        ),
        "days_ago": 90,
    },
    {
        "name": "Bella",
        "species": "dog",
        "breed": "Beagle",
        "age_years": 2,
        "gender": "female",
        "vaccinated": True,
        "neutered": False,
        "description": (
            "Cheerful Beagle with a curious nose for everything new. "
            "Gets along with other dogs and even the resident cats."
        ),
        "days_ago": 30,
    },
    {
        "name": "Charlie",
        "species": "dog",
        "breed": "Mixed Breed",
        "age_years": 8,
        "gender": "male",
        "vaccinated": True,
        "neutered": True,
        "description": (
            "Calm senior who would thrive in a quiet household. "
            "Loves naps in sunny spots and short, slow walks."
        ),
        "days_ago": 120,
    },
    {
        "name": "Mochi",
        "species": "cat",
        "breed": "Domestic Shorthair",
        "age_years": 1,
        "gender": "female",
        "vaccinated": True,
        "neutered": True,
        "description": (
            "Playful tabby kitten with a soft white belly. "
            "Loves chasing feather toys and cuddling after dinner."
        ),
        "days_ago": 20,
    },
    {
        "name": "Oliver",
        "species": "cat",
        "breed": "Maine Coon",
        "age_years": 4,
        "gender": "male",
        "vaccinated": True,
        "neutered": True,
        "description": (
            "Majestic Maine Coon with a gentle temperament and a fluffy tail. "
            "Great fit for families with older children."
        ),
        "days_ago": 60,
    },
    {
        "name": "Cleo",
        "species": "cat",
        "breed": "Siamese",
        "age_years": 6,
        "gender": "female",
        "vaccinated": True,
        "neutered": True,
        "description": (
            "Talkative Siamese who will tell you exactly what she thinks. "
            "Wants an attentive owner who enjoys conversation."
        ),
        "days_ago": 75,
    },
    {
        "name": "Pepper",
        "species": "cat",
        "breed": "Domestic Shorthair",
        "age_years": 3,
        "gender": "male",
        "vaccinated": True,
        "neutered": True,
        "description": (
            "Sleek black cat with bright green eyes. "
            "Shy on the first day, devoted by the second week."
        ),
        "days_ago": 50,
    },
    {
        "name": "Sunny",
        "species": "bird",
        "breed": "Cockatiel",
        "age_years": 2,
        "gender": "male",
        "vaccinated": False,
        "neutered": False,
        "description": (
            "Cheerful cockatiel who whistles tunes throughout the day. "
            "Already tame and hand-fed."
        ),
        "days_ago": 40,
    },
    {
        "name": "Kiwi",
        "species": "bird",
        "breed": "Budgerigar",
        "age_years": 1,
        "gender": "female",
        "vaccinated": False,
        "neutered": False,
        "description": (
            "Small green budgie with an adventurous personality. "
            "Would do best with a flying companion of her own."
        ),
        "days_ago": 25,
    },
    {
        "name": "Pebbles",
        "species": "rabbit",
        "breed": "Holland Lop",
        "age_years": 2,
        "gender": "female",
        "vaccinated": True,
        "neutered": True,
        "description": (
            "Sweet Holland Lop with floppy ears and a love for leafy greens. "
            "Litter-trained and used to apartment living."
        ),
        "days_ago": 35,
    },
    {
        "name": "Toby",
        "species": "other",
        "breed": "Guinea Pig",
        "age_years": 1,
        "gender": "male",
        "vaccinated": False,
        "neutered": False,
        "description": (
            "Friendly guinea pig who chirps with delight at fresh vegetables. "
            "Great starter pet for first-time owners."
        ),
        "days_ago": 15,
    },
]

NOTES: list[tuple[str, str]] = [
    ("Luna", "Vaccinations refreshed on intake. No allergies known."),
    ("Max", "Responds best to consistent, calm handling. Currently working on leash manners."),
    ("Mochi", "Loves Kong toys and chasing crumpled paper balls."),
]


async def _seed_users() -> tuple[User, User]:
    admin = await User.find_one(User.email == ADMIN_EMAIL)
    if admin is None:
        admin = User(
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            full_name="Shelter Admin",
            role="admin",
        )
        await admin.insert()

    user = await User.find_one(User.email == USER_EMAIL)
    if user is None:
        user = User(
            email=USER_EMAIL,
            password_hash=hash_password(USER_PASSWORD),
            full_name="Demo Adopter",
            role="user",
        )
        await user.insert()

    return admin, user


async def _seed_animals() -> list[Animal]:
    seeded: list[Animal] = []
    for entry in ANIMALS:
        existing = await Animal.find_one(Animal.name == entry["name"])
        if existing is not None:
            seeded.append(existing)
            continue
        data = dict(entry)
        days_ago = data.pop("days_ago")
        animal = Animal(arrived_at=utc_now() - timedelta(days=days_ago), **data)
        await animal.insert()
        seeded.append(animal)
    return seeded


async def _seed_notes(animals: list[Animal], admin: User) -> None:
    by_name = {a.name: a for a in animals}
    for animal_name, text in NOTES:
        animal = by_name.get(animal_name)
        if animal is None:
            continue
        existing = await AnimalNote.find_one(
            AnimalNote.animal_id == animal.id,
            AnimalNote.text == text,
        )
        if existing is None:
            await AnimalNote(animal_id=animal.id, author_id=admin.id, text=text).insert()


async def _seed_adoptions(animals: list[Animal], admin: User, user: User) -> None:
    available = [a for a in animals if a.status == "available"]
    if len(available) < 3:
        return

    for animal in available[:2]:
        existing = await AdoptionRequest.find_one(
            AdoptionRequest.animal_id == animal.id,
            AdoptionRequest.user_id == user.id,
        )
        if existing is not None:
            continue
        await AdoptionRequest(
            animal_id=animal.id,
            user_id=user.id,
            status="pending",
            message=f"I would love to give {animal.name} a forever home.",
        ).insert()
        animal.status = "pending"
        animal.updated_at = utc_now()
        await animal.save()

    approved_target = available[2]
    existing_approved = await AdoptionRequest.find_one(
        AdoptionRequest.animal_id == approved_target.id,
        AdoptionRequest.user_id == user.id,
    )
    if existing_approved is None:
        decided_at = utc_now() - timedelta(days=3)
        await AdoptionRequest(
            animal_id=approved_target.id,
            user_id=user.id,
            status="approved",
            message=f"Excited to welcome {approved_target.name} into our family.",
            decided_by_id=admin.id,
            decided_at=decided_at,
            updated_at=decided_at,
        ).insert()
        approved_target.status = "adopted"
        approved_target.updated_at = utc_now()
        await approved_target.save()


async def main() -> None:
    await init_db()
    try:
        admin, user = await _seed_users()
        animals = await _seed_animals()
        await _seed_notes(animals, admin)
        await _seed_adoptions(animals, admin, user)
        print(
            f"Seed complete: {len(animals)} animals, "
            f"admin={admin.email}, user={user.email}"
        )
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
