"""
Dependencias de FastAPI compartidas entre controladores.

Aqui vive principalmente el resolutor del usuario autenticado a partir del
header Authorization. Si el token no esta presente o es invalido, se lanza
HTTPException 401.
"""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales invalidas o token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_error

    payload = decode_access_token(token)
    if not payload:
        raise credentials_error

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_error

    user = db.query(User).filter(User.id == int(user_id), User.is_active.is_(True)).first()
    if not user:
        raise credentials_error
    return user


def get_request_context(request: Request) -> dict:
    """Recupera datos del request para enriquecer la trazabilidad."""
    client = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return {"ip_address": client, "user_agent": user_agent}
