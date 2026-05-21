"""
Punto de entrada de la API.

Se configuran CORS, los routers de cada modulo y un endpoint de health para
poder validar de forma rapida que la aplicacion responde y la BD esta arriba.
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.controllers.auth_controller import router as auth_router
from app.controllers.payment_method_controller import router as payment_methods_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Wallet API",
        description=(
            "API para administrar metodos de pago de forma segura. "
            "Cuenta con autenticacion por JWT, cifrado simetrico de identificadores "
            "y trazabilidad de operaciones relevantes."
        ),
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)
    app.include_router(payment_methods_router)

    @app.get("/health", tags=["health"], status_code=status.HTTP_200_OK)
    def health() -> dict:
        db_ok = True
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception:
            db_ok = False
        return {"status": "ok" if db_ok else "degraded", "database": db_ok}

    return app


app = create_app()
