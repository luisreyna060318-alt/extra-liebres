"""carreras oficiales

Las carreras pasan a ser una lista fija (backend/app/core/constantes.py). Esta migración solo cambia datos: renombra
las carreras que ya estaban guardadas (las del seed, que son ficticias) a los nombres oficiales. No cambia el esquema.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-22 04:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (nombre anterior, nombre oficial)
CAMBIOS = [
    ("Ingeniería en Sistemas Computacionales", "ING. SISTEMAS COMPUTACIONALES"),
    ("Ingeniería Industrial", "ING. INDUSTRIAL"),
    ("Ingeniería Electrónica", "ING. ELECTRÓNICA"),
    ("Ingeniería Eléctrica", "ING. ELÉCTRICA"),
    ("Ingeniería Mecánica", "ING. MECÁNICA"),
    ("Ingeniería Mecatrónica", "ING. MECATRÓNICA"),
    ("Ingeniería en Gestión Empresarial", "ING. EN GESTIÓN EMPRESARIAL"),
    ("Ingeniería Química", "ING. LOGÍSTICA"),
    ("Arquitectura", "LIC. ADMINISTRACIÓN"),
    ("Ingeniería Civil", "CONTADOR PÚBLICO"),
]


def upgrade() -> None:
    """Upgrade schema."""
    conexion = op.get_bind()
    for anterior, oficial in CAMBIOS:
        conexion.execute(
            sa.text("UPDATE alumno SET carrera = :oficial WHERE carrera = :anterior"),
            {"oficial": oficial, "anterior": anterior},
        )


def downgrade() -> None:
    """Downgrade schema."""
    # Los nombres anteriores no se pueden recuperar con exactitud (tres carreras se reasignaron), así que no se deshace.
    pass
