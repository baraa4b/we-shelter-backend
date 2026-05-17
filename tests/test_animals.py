import pytest
from httpx import AsyncClient


def _new_animal_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "name": "Rex",
        "species": "dog",
        "breed": "Mixed",
        "ageYears": 4,
        "gender": "male",
        "vaccinated": True,
        "neutered": False,
        "description": "Calm brown dog who walks well on a leash.",
        "arrivedAt": "2026-01-15T00:00:00Z",
    }
    payload.update(overrides)
    return payload


@pytest.mark.asyncio
async def test_anonymous_list_and_filter(client: AsyncClient, admin_token: str) -> None:
    headers = {"Authorization": f"Bearer {admin_token}"}
    await client.post("/admin/animals", json=_new_animal_payload(name="Rex", species="dog"), headers=headers)
    await client.post("/admin/animals", json=_new_animal_payload(name="Mochi", species="cat", gender="female"), headers=headers)

    listing = await client.get("/animals")
    assert listing.status_code == 200
    body = listing.json()
    assert body["page"] == 1
    assert body["pageSize"] == 20
    assert body["total"] >= 2
    assert len(body["items"]) >= 2

    cats_only = await client.get("/animals", params={"species": "cat"})
    assert cats_only.status_code == 200
    assert all(item["species"] == "cat" for item in cats_only.json()["items"])


@pytest.mark.asyncio
async def test_admin_create_get_delete(client: AsyncClient, admin_token: str) -> None:
    headers = {"Authorization": f"Bearer {admin_token}"}
    created = await client.post("/admin/animals", json=_new_animal_payload(), headers=headers)
    assert created.status_code == 201
    animal_id = created.json()["id"]

    fetched = await client.get(f"/animals/{animal_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Rex"

    deleted = await client.delete(f"/admin/animals/{animal_id}", headers=headers)
    assert deleted.status_code == 204

    missing = await client.get(f"/animals/{animal_id}")
    assert missing.status_code == 404
    assert missing.json()["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_non_admin_cannot_create(client: AsyncClient, user_token: str) -> None:
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await client.post("/admin/animals", json=_new_animal_payload(), headers=headers)
    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"
