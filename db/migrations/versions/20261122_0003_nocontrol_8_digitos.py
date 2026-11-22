"""números de control de 8 dígitos

El número de control pasa a ser de exactamente 8 dígitos y no mayor a 26999999 (se valida en la API). Esta migración
solo cambia datos: los alumnos del seed (ficticios) tenían números como 99000001; pasan a 26000001. Como
alumno_grupo.nocontrol apunta a alumno.nocontrol, la llave foránea se quita un momento para cambiar las dos tablas
y se vuelve a crear igual.

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-22 17:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, Sequence[str], None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Los números del seed: "99" y seis dígitos (99000001). Se les cambia el prefijo: 99000001 -> 26000001
CAMBIO = "UPDATE {tabla} SET nocontrol = '26' || substr(nocontrol, 3) WHERE nocontrol LIKE '99%' AND length(nocontrol) = 8"


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('fk_alumno_grupo_nocontrol_alumno', 'alumno_grupo', type_='foreignkey')
    op.execute(sa.text(CAMBIO.format(tabla='alumno_grupo')))
    op.execute(sa.text(CAMBIO.format(tabla='alumno')))
    op.create_foreign_key(
        'fk_alumno_grupo_nocontrol_alumno', 'alumno_grupo', 'alumno', ['nocontrol'], ['nocontrol'], ondelete='RESTRICT'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Los números anteriores no se pueden distinguir de los alumnos nuevos que empiecen con 26, así que no se deshace.
    pass
