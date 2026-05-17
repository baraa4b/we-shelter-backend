import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_login_me_refresh(client: AsyncClient) -> None:
    register = await client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "password": "Wonderland1!",
            "fullName": "Alice Liddell",
        },
    )
    assert register.status_code == 201
    body = register.json()
    assert body["user"]["email"] == "alice@example.com"
    assert body["user"]["role"] == "user"
    assert body["accessToken"]
    refresh_token = body["refreshToken"]

    login = await client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": "Wonderland1!"},
    )
    assert login.status_code == 200
    access_token = login.json()["accessToken"]

    me = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "alice@example.com"

    refreshed = await client.post(
        "/auth/refresh",
        json={"refreshToken": refresh_token},
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["accessToken"]


@pytest.mark.asyncio
async def test_login_rejects_bad_password(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={
            "email": "bob@example.com",
            "password": "RightOne1!",
            "fullName": "Bob",
        },
    )
    bad = await client.post(
        "/auth/login",
        json={"email": "bob@example.com", "password": "WrongOne1!"},
    )
    assert bad.status_code == 401
    assert bad.json()["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_me_requires_bearer(client: AsyncClient) -> None:
    response = await client.get("/auth/me")
    assert response.status_code == 401
