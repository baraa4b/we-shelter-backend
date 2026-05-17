from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mongodb_uri: str = Field(alias="MONGODB_URI")
    mongodb_db: str = Field(alias="MONGODB_DB")
    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_access_ttl_min: int = Field(default=30, alias="JWT_ACCESS_TTL_MIN")
    jwt_refresh_ttl_days: int = Field(default=7, alias="JWT_REFRESH_TTL_DAYS")
    allowed_origins: str = Field(default="*", alias="ALLOWED_ORIGINS")
    dev_key: str = Field(default="", alias="DEV_KEY")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
