import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import pytest_asyncio
from beanie import init_beanie
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

os.environ.setdefault("MONGODB_URI", "mongodb://test-not-used")
os.environ.setdefault("MONGODB_DB", "shelter_test")
os.environ.setdefault("JWT_SECRET", "test-secret-key-not-for-production-use-only")
os.environ.setdefault("ALLOWED_ORIGINS", "*")

from db.adoption import AdoptionRequest  # noqa: E402
from db.animal import Animal  # noqa: E402
from db.favorite import Favorite  # noqa: E402
from db.image import AnimalImage  # noqa: E402
from db.note import AnimalNote  # noqa: E402
from db.user import User  # noqa: E402
from main import create_app  # noqa: E402


DOCUMENT_MODELS = [User, Animal, AdoptionRequest, AnimalNote, AnimalImage, Favorite]


@asynccontextmanager
async def _noop_lifespan(_app: FastAPI):
    yield


@pytest_asyncio.fixture
async def app() -> AsyncIterator[FastAPI]:
    mock_client = AsyncMongoMockClient()
    database = mock_client["shelter_test"]
    await init_beanie(database=database, document_models=DOCUMENT_MODELS)
    yield create_app(lifespan=_noop_lifespan)


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def user_token(client: AsyncClient) -> str:
    response = await client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "User1234!",
            "fullName": "Normal User",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["accessToken"]


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient) -> str:
    response = await client.post(
        "/auth/register",
        json={
            "email": "admin@example.com",
            "password": "Admin1234!",
            "fullName": "Admin User",
        },
    )
    assert response.status_code == 201, response.text
    user_id = response.json()["user"]["id"]

    from beanie import PydanticObjectId

    admin = await User.get(PydanticObjectId(user_id))
    assert admin is not None
    admin.role = "admin"
    await admin.save()

    login_resp = await client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "Admin1234!"},
    )
    assert login_resp.status_code == 200, login_resp.text
    return login_resp.json()["accessToken"]
