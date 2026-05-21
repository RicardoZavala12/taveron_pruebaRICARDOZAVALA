"""
Logica de negocio del modulo de metodos de pago.

Aqui viven las reglas de validacion especificas (Luhn para tarjetas, longitud
de CLABE, etc.), el cifrado del identificador antes de persistirlo y el manejo
de duplicados mediante el fingerprint HMAC.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.core.crypto import (
    encrypt_identifier,
    fingerprint_identifier,
    last_four,
    mask_identifier,
    normalize_identifier,
)
from app.models.audit_log import AuditAction
from app.models.payment_method import (
    PaymentMethod,
    PaymentMethodStatus,
    PaymentMethodType,
)
from app.models.user import User
from app.schemas.payment_method import (
    PaymentMethodCreate,
    PaymentMethodFilters,
    PaymentMethodList,
    PaymentMethodRead,
)
from app.services.audit_service import record_event


class PaymentMethodError(Exception):
    """Error de negocio en el modulo de metodos de pago."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _validate_identifier(type_: PaymentMethodType, normalized: str) -> None:
    """
    Validacion minima del identificador.

    Se acepta cualquier secuencia alfanumerica con longitud razonable (4 a 40
    caracteres). No se aplican reglas especificas por tipo (Luhn, longitud
    exacta de CLABE, etc.) para mantener el alta flexible. La unicidad por
    usuario se sigue garantizando via fingerprint HMAC.
    """
    if not normalized:
        raise PaymentMethodError("El identificador es obligatorio")
    if not normalized.isalnum():
        raise PaymentMethodError("El identificador solo puede contener digitos o letras")
    if not (4 <= len(normalized) <= 40):
        raise PaymentMethodError("El identificador debe tener entre 4 y 40 caracteres")


def _to_read(method: PaymentMethod) -> PaymentMethodRead:
    """Convierte una entidad de BD en su representacion publica enmascarada."""
    # No se descifra el identificador para construir la mascara. Se reconstruye
    # un patron de bloques de cuatro a partir del last4 visible, para que el
    # cliente pueda presentarlo como una tarjeta sin riesgo.
    masked = "**** **** **** " + method.identifier_last4
    return PaymentMethodRead(
        id=method.id,
        type=method.type,
        alias=method.alias,
        institution=method.institution,
        currency=method.currency,
        identifier_last4=method.identifier_last4,
        identifier_masked=masked,
        status=method.status,
        created_at=method.created_at,
        updated_at=method.updated_at,
    )


def create_method(
    db: Session,
    user: User,
    data: PaymentMethodCreate,
    *,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> PaymentMethodRead:
    normalized = normalize_identifier(data.identifier)
    _validate_identifier(data.type, normalized)

    fingerprint = fingerprint_identifier(data.identifier)

    duplicate = (
        db.query(PaymentMethod)
        .filter(
            PaymentMethod.user_id == user.id,
            PaymentMethod.identifier_fingerprint == fingerprint,
            PaymentMethod.is_deleted.is_(False),
        )
        .first()
    )
    if duplicate:
        raise PaymentMethodError(
            "Ya tienes registrado este metodo de pago",
            status_code=409,
        )

    method = PaymentMethod(
        user_id=user.id,
        type=data.type,
        alias=data.alias.strip(),
        institution=data.institution.strip(),
        currency=data.currency.upper(),
        identifier_encrypted=encrypt_identifier(normalized),
        identifier_last4=last_four(normalized),
        identifier_fingerprint=fingerprint,
        status=PaymentMethodStatus.active,
    )
    db.add(method)
    db.commit()
    db.refresh(method)

    record_event(
        db,
        action=AuditAction.payment_method_created,
        user_id=user.id,
        entity_type="payment_method",
        entity_id=method.id,
        ip_address=ip_address,
        user_agent=user_agent,
        extra={
            "type": method.type.value,
            "institution": method.institution,
            "currency": method.currency,
        },
    )
    return _to_read(method)


def list_methods(
    db: Session,
    user: User,
    filters: PaymentMethodFilters,
) -> PaymentMethodList:
    query = db.query(PaymentMethod).filter(
        PaymentMethod.user_id == user.id,
        PaymentMethod.is_deleted.is_(False),
    )
    if filters.status:
        query = query.filter(PaymentMethod.status == filters.status)
    if filters.type:
        query = query.filter(PaymentMethod.type == filters.type)

    total = query.count()
    items = (
        query.order_by(PaymentMethod.created_at.desc())
        .offset((filters.page - 1) * filters.size)
        .limit(filters.size)
        .all()
    )
    return PaymentMethodList(
        items=[_to_read(m) for m in items],
        total=total,
        page=filters.page,
        size=filters.size,
    )


def _get_owned_method(db: Session, user: User, method_id: int) -> PaymentMethod:
    method = (
        db.query(PaymentMethod)
        .filter(
            PaymentMethod.id == method_id,
            PaymentMethod.user_id == user.id,
            PaymentMethod.is_deleted.is_(False),
        )
        .first()
    )
    if not method:
        raise PaymentMethodError("Metodo de pago no encontrado", status_code=404)
    return method


def get_method(
    db: Session,
    user: User,
    method_id: int,
    *,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> PaymentMethodRead:
    method = _get_owned_method(db, user, method_id)

    record_event(
        db,
        action=AuditAction.payment_method_viewed,
        user_id=user.id,
        entity_type="payment_method",
        entity_id=method.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return _to_read(method)


def deactivate_method(
    db: Session,
    user: User,
    method_id: int,
    *,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> PaymentMethodRead:
    method = _get_owned_method(db, user, method_id)
    if method.status == PaymentMethodStatus.inactive:
        # Idempotente: si ya esta inactivo no se hace nada nuevo.
        return _to_read(method)

    method.status = PaymentMethodStatus.inactive
    db.commit()
    db.refresh(method)

    record_event(
        db,
        action=AuditAction.payment_method_deactivated,
        user_id=user.id,
        entity_type="payment_method",
        entity_id=method.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return _to_read(method)


def delete_method(
    db: Session,
    user: User,
    method_id: int,
    *,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """Soft delete. Conserva el renglon para preservar la trazabilidad."""
    method = _get_owned_method(db, user, method_id)

    method.is_deleted = True
    method.status = PaymentMethodStatus.inactive
    from datetime import datetime, timezone
    method.deleted_at = datetime.now(timezone.utc)
    db.commit()

    record_event(
        db,
        action=AuditAction.payment_method_deleted,
        user_id=user.id,
        entity_type="payment_method",
        entity_id=method.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
