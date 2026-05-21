"""
Modelo del metodo de pago.

Se separa de forma intencional el identificador en tres columnas:

- `identifier_encrypted`: el valor completo cifrado con Fernet. Es lo unico
  que permite recuperar el dato original y solo se descifra cuando es
  estrictamente necesario.
- `identifier_last4`: los ultimos cuatro caracteres en claro, usados para
  mostrar al usuario sin necesidad de descifrar.
- `identifier_fingerprint`: HMAC-SHA256 del identificador normalizado. Sirve
  para detectar duplicados (unicidad por usuario) sin exponer el dato.

El soft delete se maneja con `is_deleted` y `deleted_at` para conservar
historicos sin perder trazabilidad.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class PaymentMethodType(str, enum.Enum):
    card = "card"
    bank_account = "bank_account"
    clabe = "clabe"
    other = "other"


class PaymentMethodStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    type = Column(Enum(PaymentMethodType, name="payment_method_type"), nullable=False)
    alias = Column(String(80), nullable=False)
    institution = Column(String(120), nullable=False)
    currency = Column(String(3), nullable=False)

    identifier_encrypted = Column(String(512), nullable=False)
    identifier_last4 = Column(String(4), nullable=False)
    identifier_fingerprint = Column(String(64), nullable=False, index=True)

    status = Column(
        Enum(PaymentMethodStatus, name="payment_method_status"),
        nullable=False,
        default=PaymentMethodStatus.active,
        server_default=PaymentMethodStatus.active.value,
    )

    is_deleted = Column(Boolean, nullable=False, default=False, server_default="false")
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", back_populates="payment_methods")

    __table_args__ = (
        # Un mismo usuario no puede registrar dos veces el mismo identificador activo.
        # El soft delete se contempla incluyendo `is_deleted` en el constraint.
        UniqueConstraint(
            "user_id",
            "identifier_fingerprint",
            "is_deleted",
            name="uq_payment_method_user_fingerprint_alive",
        ),
        Index("ix_payment_methods_user_status", "user_id", "status"),
    )
