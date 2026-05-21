"""
Configuracion compartida de pytest.

Para correr los tests sin necesidad de PostgreSQL se monta una base SQLite en
memoria compartida. Como el resto de la aplicacion crea su propio engine y su
propia SessionLocal al importar `app.core.database`, en este conftest se
reemplazan ambos por versiones que apuntan al SQLite de prueba antes de
importar la app.
"""

import os

from cryptography.fernet import Fernet


# Variables de entorno minimas que necesita `Settings` para inicializarse.
os.environ.setdefault("APP_ENV", "testing")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_wallet.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRE_MINUTES", "60")
os.environ.setdefault("FERNET_KEY", Fernet.generate_key().decode())
os.environ.setdefault("FINGERPRINT_PEPPER", "test-pepper")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")


import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import database as db_module


# Engine SQLite en memoria. StaticPool conserva una unica conexion para que
# las tablas creadas se vean en todos los hilos del TestClient.
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(test_engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# Se reemplazan engine y SessionLocal del modulo de base de datos para que la
# aplicacion completa use el SQLite en memoria.
db_module.engine = test_engine
db_module.SessionLocal = TestingSessionLocal


from app.core.database import Base, get_db
from app.main import app


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client():
    def _override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    """Crea un usuario y devuelve sus credenciales en claro."""
    payload = {
        "email": "diana@example.com",
        "full_name": "Diana Prueba",
        "password": "Sup3rSecreta!",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201, response.text
    return payload


@pytest.fixture
def auth_token(client, registered_user):
    response = client.post(
        "/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
