"""
Endpoints de autenticacion y perfil.

El router se monta bajo el prefijo /auth (registro, login, logout) y /users
para la consulta del perfil propio.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, get_request_context
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    PasswordChangeRequest,
    TokenResponse,
    UserCreate,
    UserRead,
)
from app.services import auth_service


router = APIRouter()


@router.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=["auth"])
def register(
    data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> UserRead:
    context = get_request_context(request)
    try:
        return auth_service.register_user(db, data, **context)
    except auth_service.AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    context = get_request_context(request)
    try:
        return auth_service.authenticate(db, data, **context)
    except auth_service.AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT, tags=["auth"])
def logout(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    context = get_request_context(request)
    auth_service.logout(db, user, **context)


@router.get("/users/me", response_model=UserRead, tags=["users"])
def get_profile(user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(user)


@router.put(
    "/users/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["users"],
)
def change_password(
    data: PasswordChangeRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    context = get_request_context(request)
    try:
        auth_service.change_password(db, user, data, **context)
    except auth_service.AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
