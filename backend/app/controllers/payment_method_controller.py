"""
Endpoints REST para administrar metodos de pago.

Todas las rutas viven bajo /payment-methods y exigen un usuario autenticado.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, get_request_context
from app.models.user import User
from app.models.payment_method import PaymentMethodStatus, PaymentMethodType
from app.schemas.payment_method import (
    PaymentMethodCreate,
    PaymentMethodFilters,
    PaymentMethodList,
    PaymentMethodRead,
)
from app.services import payment_method_service as pm_service


router = APIRouter(prefix="/payment-methods", tags=["payment-methods"])


@router.get("", response_model=PaymentMethodList)
def list_methods(
    request: Request,
    status_filter: PaymentMethodStatus | None = Query(default=None, alias="status"),
    type_filter: PaymentMethodType | None = Query(default=None, alias="type"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PaymentMethodList:
    filters = PaymentMethodFilters(status=status_filter, type=type_filter, page=page, size=size)
    return pm_service.list_methods(db, user, filters)


@router.post("", response_model=PaymentMethodRead, status_code=status.HTTP_201_CREATED)
def create_method(
    data: PaymentMethodCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PaymentMethodRead:
    context = get_request_context(request)
    try:
        return pm_service.create_method(db, user, data, **context)
    except pm_service.PaymentMethodError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/{method_id}", response_model=PaymentMethodRead)
def get_method(
    method_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PaymentMethodRead:
    context = get_request_context(request)
    try:
        return pm_service.get_method(db, user, method_id, **context)
    except pm_service.PaymentMethodError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.patch("/{method_id}/deactivate", response_model=PaymentMethodRead)
def deactivate_method(
    method_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PaymentMethodRead:
    context = get_request_context(request)
    try:
        return pm_service.deactivate_method(db, user, method_id, **context)
    except pm_service.PaymentMethodError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.delete("/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_method(
    method_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    context = get_request_context(request)
    try:
        pm_service.delete_method(db, user, method_id, **context)
    except pm_service.PaymentMethodError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
