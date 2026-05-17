import pytest
from httpx import AsyncClient


_ANIMAL = {
    "name": "Rocky",
    "species": "dog",
    "breed": "Boxer",
    "ageYears": 3,
    "gender": "male",
    "vaccinated": True,
    "neutered": True,
    "description": "Energetic boxer mix, great with kids.",
    "arrivedAt": "2026-03-01T00:00:00Z",
}


async def _create_animal(client: AsyncClient, admin_token: str, **overrides: object) -> str:
    payload = {**_ANIMAL, **overrides}
    response = await client.post(
        "/admin/animals",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


@pytest.mark.asyncio
async def test_approved_flow_sets_animal_to_adopted(
    client: AsyncClient,
    admin_token: str,
    user_token: str,
) -> None:
    animal_id = await _create_animal(client, admin_token)
    user_headers = {"Authorization": f"Bearer {user_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    request = await client.post(
        "/adoptions",
        json={"animalId": animal_id, "message": "Please consider me."},
        headers=user_headers,
    )
    assert request.status_code == 201
    request_id = request.json()["id"]

    assert (await client.get(f"/animals/{animal_id}")).json()["status"] == "pending"

    approved = await client.patch(
        f"/admin/adoptions/{request_id}",
        json={"status": "approved"},
        headers=admin_headers,
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    assert (await client.get(f"/animals/{animal_id}")).json()["status"] == "adopted"


@pytest.mark.asyncio
async def test_rejected_flow_returns_animal_to_available(
    client: AsyncClient,
    admin_token: str,
    user_token: str,
) -> None:
    animal_id = await _create_animal(client, admin_token, name="Daisy")
    user_headers = {"Authorization": f"Bearer {user_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    request = await client.post(
        "/adoptions",
        json={"animalId": animal_id},
        headers=user_headers,
    )
    request_id = request.json()["id"]

    rejected = await client.patch(
        f"/admin/adoptions/{request_id}",
        json={"status": "rejected"},
        headers=admin_headers,
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"

    animal = (await client.get(f"/animals/{animal_id}")).json()
    assert animal["status"] == "available"


@pytest.mark.asyncio
async def test_cannot_adopt_when_not_available(
    client: AsyncClient,
    admin_token: str,
    user_token: str,
) -> None:
    animal_id = await _create_animal(client, admin_token, name="Buddy")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    first = await client.post("/adoptions", json={"animalId": animal_id}, headers=user_headers)
    assert first.status_code == 201

    second = await client.post("/adoptions", json={"animalId": animal_id}, headers=user_headers)
    assert second.status_code == 409
    assert second.json()["code"] == "CONFLICT"
