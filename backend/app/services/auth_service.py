"""
Logica de negocio para registro y autenticacion de usuarios.

El controlador delega aqui para mantenerse delgado. Las reglas (correo unico,
validacion de credenciales, generacion de token) viven en este servicio.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.audit_log import AuditAction
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    PasswordChangeRequest,
    TokenResponse,
    UserCreate,
    UserRead,
)
from app.services.audit_service import record_event


class AuthError(Exception):
    """Error de negocio en el flujo de autenticacion."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def register_user(
    db: Session,
    data: UserCreate,
    *,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> UserRead:
    existing = db.query(User).filter(User.email == data.email.lower()).first()
    if existing:
        raise AuthError("Ya existe un usuario con ese correo", status_code=409)

    user = User(
        email=data.email.lower(),
        full_name=data.full_name.strip(),
        password_hash=hash_password(data.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    record_event(
        db,
        action=AuditAction.user_registered,
        user_id=user.id,
        entity_type="user",
        entity_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return UserRead.model_validate(user)


def authenticate(
    db: Session,
    data: LoginRequest,
    *,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> TokenResponse:
    user = db.query(User).filter(User.email == data.email.lower()).first()

    if not user or not verify_password(data.password, user.password_hash):
        # Aun sin usuario valido se registra el intento fallido para trazabilidad.
        record_event(
            db,
            action=AuditAction.user_login_failed,
            user_id=user.id if user else None,
            entity_type="user",
            entity_id=user.id if user else None,
            ip_address=ip_address,
            user_agent=user_agent,
            extra={"email": data.email.lower()},
        )
        raise AuthError("Credenciales invalidas", status_code=401)

    if not user.is_active:
        raise AuthError("La cuenta esta deshabilitada", status_code=403)

    token = create_access_token(subject=str(user.id))

    record_event(
        db,
        action=AuditAction.user_login_success,
        user_id=user.id,
        entity_type="user",
        entity_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.JWT_EXPIRE_MINUTES,
        user=UserRead.model_validate(user),
    )


def logout(
    db: Session,
    user: User,
    *,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    # Con JWT sin lista negra, el logout es informativo: el cliente descarta el
    # token y se registra el evento para auditoria.
    record_event(
        db,
        action=AuditAction.user_logout,
        user_id=user.id,
        entity_type="user",
        entity_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )


def change_password(
    db: Session,
    user: User,
    data: PasswordChangeRequest,
    *,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """
    Cambia la contrasena del usuario autenticado.

    Se exige la contrasena actual para evitar que un token robado, sin conocer
    el secreto del usuario, pueda tomar control de la cuenta. Tanto los
    intentos exitosos como los fallidos quedan registrados en auditoria.
    """
    if not verify_password(data.current_password, user.password_hash):
        record_event(
            db,
            action=AuditAction.user_password_change_failed,
            user_id=user.id,
            entity_type="user",
            entity_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            extra={"reason": "current_password_mismatch"},
        )
        raise AuthError("La contrasena actual no es correcta", status_code=400)

    if verify_password(data.new_password, user.password_hash):
        raise AuthError(
            "La nueva contrasena debe ser distinta a la actual",
            status_code=400,
        )

    user.password_hash = hash_password(data.new_password)
    db.commit()

    record_event(
        db,
        action=AuditAction.user_password_changed,
        user_id=user.id,
        entity_type="user",
        entity_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
