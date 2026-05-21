"""Agrega acciones de auditoria para cambio de contrasena

Revision ID: 0002_password_change_audit
Revises: 0001_initial
Create Date: 2026-05-21

"""
from typing import Sequence, Union

from alembic import op


revision: str = "0002_password_change_audit"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Postgres exige ALTER TYPE ... ADD VALUE para sumar valores al enum.
    # No es transaccional, asi que se ejecuta fuera de la transaccion implicita.
    connection = op.get_bind()
    dialect_name = connection.dialect.name
    if dialect_name == "postgresql":
        op.execute("ALTER TYPE audit_action ADD VALUE IF NOT EXISTS 'user_password_changed'")
        op.execute(
            "ALTER TYPE audit_action ADD VALUE IF NOT EXISTS 'user_password_change_failed'"
        )
    # En SQLite (usado en tests) los enums se manejan como CHECK y SQLAlchemy
    # los lee de la definicion del modelo, asi que no hace falta tocar nada.


def downgrade() -> None:
    # Postgres no permite eliminar valores de un enum de forma trivial.
    # Si fuera estrictamente necesario habria que recrear el tipo.
    pass
