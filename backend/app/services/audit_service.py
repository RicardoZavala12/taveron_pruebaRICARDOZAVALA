"""
Servicio de trazabilidad.

Encapsula la insercion de filas en la tabla `audit_logs` para que los demas
servicios no acoplen su logica a la forma de persistir la bitacora.
"""

from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditAction, AuditLog


def record_event(
    db: Session,
    *,
    action: AuditAction,
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    extra: Optional[dict[str, Any]] = None,
    commit: bool = True,
) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        ip_address=ip_address,
        user_agent=(user_agent or "")[:255] or None,
        extra=extra,
    )
    db.add(log)
    if commit:
        db.commit()
        db.refresh(log)
    else:
        db.flush()
    return log
