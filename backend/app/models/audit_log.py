"""
Modelo de trazabilidad.

Cada operacion relevante (registro, login, alta/baja/desactivacion de metodo
de pago, etc.) deja un renglon en esta tabla. Sirve como bitacora de auditoria
y nunca se modifica una vez insertada.
"""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AuditAction(str, enum.Enum):
    user_registered = "user_registered"
    user_login_success = "user_login_success"
    user_login_failed = "user_login_failed"
    user_logout = "user_logout"
    user_password_changed = "user_password_changed"
    user_password_change_failed = "user_password_change_failed"
    payment_method_created = "payment_method_created"
    payment_method_viewed = "payment_method_viewed"
    payment_method_deactivated = "payment_method_deactivated"
    payment_method_deleted = "payment_method_deleted"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    action = Column(Enum(AuditAction, name="audit_action"), nullable=False, index=True)
    entity_type = Column(String(60), nullable=True)
    entity_id = Column(Integer, nullable=True)

    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    extra = Column("metadata", JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user = relationship("User", back_populates="audit_logs")
