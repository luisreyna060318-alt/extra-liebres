"""rol lector

Las cuentas que se crean desde el registro ahora nacen con el rol "lector" (solo ve el tablero y las listas). La
restricción de la tabla usuario se reemplaza para aceptar los tres roles. Las cuentas que ya existen conservan su rol.

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-22 19:00:00

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '0004'
down_revision: Union[str, Sequence[str], None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# op.f() le dice a Alembic que el nombre ya trae el prefijo de la convención (ck_usuario_...) y no lo repita
def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(op.f('ck_usuario_rol_valido'), 'usuario', type_='check')
    op.create_check_constraint(
        op.f('ck_usuario_rol_valido'), 'usuario', "rol IN ('administrador', 'capturista', 'lector')"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # El rol anterior no existe: los lectores pasan a capturista pero SUSPENDIDOS, para que nadie gane permisos al
    # deshacer la migración (un administrador los reactiva uno por uno si quiere)
    op.execute("UPDATE usuario SET rol = 'capturista', activo = false WHERE rol = 'lector'")
    op.drop_constraint(op.f('ck_usuario_rol_valido'), 'usuario', type_='check')
    op.create_check_constraint(op.f('ck_usuario_rol_valido'), 'usuario', "rol IN ('administrador', 'capturista')")
