from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from db.client import close_db, init_db
from db.indexes import ensure_indexes
from routes import auth, dev
from routes.admin import adoptions as admin_adoptions
from routes.admin import animals as admin_animals
from routes.admin import notes as admin_notes
from routes.admin import statistics as admin_statistics
from routes.admin import users as admin_users
from routes.public import animals as public_animals
from routes.public import images as public_images
from routes.user import adoptions as user_adoptions
from routes.user import favorites as user_favorites
from utils.errors import AppError


Lifespan = Callable[[FastAPI], AsyncIterator[None]]


@asynccontextmanager
async def default_lifespan(_app: FastAPI) -> AsyncIterator[None]:
    await init_db()
    await ensure_indexes()
    try:
        yield
    finally:
        await close_db()


def create_app(lifespan: Lifespan | None = default_lifespan) -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Animal Shelter API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def _app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "code": exc.code},
        )

    app.include_router(auth.router)
    app.include_router(public_animals.router)
    app.include_router(public_images.router)
    app.include_router(user_adoptions.router)
    app.include_router(user_favorites.router)
    app.include_router(admin_animals.router)
    app.include_router(admin_adoptions.router)
    app.include_router(admin_notes.router)
    app.include_router(admin_statistics.router)
    app.include_router(admin_users.router)
    app.include_router(dev.router)

    return app


app = create_app()
