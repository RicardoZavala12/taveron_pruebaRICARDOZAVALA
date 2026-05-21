"""
Configuracion central de la aplicacion.

Las variables se leen del entorno (o del archivo .env si existe). Se exponen a
traves de una instancia singleton `settings` que el resto del proyecto importa.
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_ENV: str = "development"

    DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    FERNET_KEY: str
    FINGERPRINT_PEPPER: str

    CORS_ORIGINS: str = "http://localhost:5173"

    @field_validator("CORS_ORIGINS")
    @classmethod
    def split_origins(cls, value: str) -> str:
        # Se mantiene como string para no romper el tipo pero se valida que sea no vacio.
        if not value or not value.strip():
            raise ValueError("CORS_ORIGINS no puede estar vacio")
        return value

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_testing(self) -> bool:
        return self.APP_ENV.lower() == "testing"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
