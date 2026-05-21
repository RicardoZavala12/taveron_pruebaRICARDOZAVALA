"""
Schemas Pydantic para el flujo de autenticacion y perfil de usuario.

La separacion entre `UserCreate`, `UserRead` y `UserInDB` permite que el hash de
la contrasena nunca salga del servidor y que el cliente no pueda enviar campos
controlados por el sistema (id, fechas, etc.).
"""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


PasswordStr = Annotated[str, Field(min_length=8, max_length=128)]


class UserCreate(BaseModel):
    email: EmailStr
    full_name: Annotated[str, Field(min_length=2, max_length=120)]
    password: PasswordStr

    @field_validator("password")
    @classmethod
    def password_complexity(cls, value: str) -> str:
        # Se exige al menos un digito y una letra para evitar contrasenas demasiado triviales.
        has_letter = any(ch.isalpha() for ch in value)
        has_digit = any(ch.isdigit() for ch in value)
        if not (has_letter and has_digit):
            raise ValueError("La contrasena debe incluir al menos una letra y un numero")
        return value


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: UserRead


class PasswordChangeRequest(BaseModel):
    current_password: Annotated[str, Field(min_length=1, max_length=128)]
    new_password: PasswordStr

    @field_validator("new_password")
    @classmethod
    def new_password_complexity(cls, value: str) -> str:
        has_letter = any(ch.isalpha() for ch in value)
        has_digit = any(ch.isdigit() for ch in value)
        if not (has_letter and has_digit):
            raise ValueError("La nueva contrasena debe incluir al menos una letra y un numero")
        return value
