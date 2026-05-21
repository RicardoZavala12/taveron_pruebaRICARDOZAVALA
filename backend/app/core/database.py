"""
Conexion a la base de datos y sesion de SQLAlchemy.

Se expone una factory `SessionLocal` y un generador `get_db` pensado para usarse
como dependencia de FastAPI en los controladores.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    future=True,
)

Base = declarative_base()


def get_db() -> Generator:
    """Dependencia de FastAPI que entrega una sesion por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
