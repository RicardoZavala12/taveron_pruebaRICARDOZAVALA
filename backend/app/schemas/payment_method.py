"""
Schemas para los metodos de pago.

`PaymentMethodCreate` recibe el identificador en claro y los datos visibles.
`PaymentMethodRead` jamas expone el identificador completo: solo el last4 y la
mascara generada en el servidor.
"""

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.payment_method import PaymentMethodStatus, PaymentMethodType


CURRENCY_PATTERN = r"^[A-Z]{3}$"


class PaymentMethodCreate(BaseModel):
    type: PaymentMethodType
    alias: Annotated[str, Field(min_length=2, max_length=80)]
    institution: Annotated[str, Field(min_length=2, max_length=120)]
    currency: Annotated[str, Field(pattern=CURRENCY_PATTERN)]
    identifier: Annotated[str, Field(min_length=4, max_length=40)]

    @field_validator("identifier")
    @classmethod
    def identifier_basic_shape(cls, value: str) -> str:
        # Quita espacios y guiones para facilitar la validacion posterior.
        cleaned = value.replace(" ", "").replace("-", "")
        if not cleaned.isalnum():
            raise ValueError("El identificador solo puede contener digitos o letras")
        return cleaned


class PaymentMethodRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: PaymentMethodType
    alias: str
    institution: str
    currency: str
    identifier_last4: str
    identifier_masked: str
    status: PaymentMethodStatus
    created_at: datetime
    updated_at: datetime


class PaymentMethodList(BaseModel):
    items: list[PaymentMethodRead]
    total: int
    page: int
    size: int


class PaymentMethodFilters(BaseModel):
    status: Optional[PaymentMethodStatus] = None
    type: Optional[PaymentMethodType] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
