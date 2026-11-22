from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.grupo import Grupo


class Semestre(Base):
    """Periodo académico en el que se impartió un grupo (por ejemplo, enero a junio de 2026)."""

    __tablename__ = "semestre"

    idsemestre: Mapped[int] = mapped_column(primary_key=True)
    mesinicio: Mapped[int]  # 1 a 12
    mestermino: Mapped[int]  # 1 a 12
    anio: Mapped[int]

    grupos: Mapped[list["Grupo"]] = relationship(back_populates="semestre")

    __table_args__ = (
        CheckConstraint("mesinicio BETWEEN 1 AND 12", name="mesinicio_valido"),
        CheckConstraint("mestermino BETWEEN 1 AND 12", name="mestermino_valido"),
        # No puede haber dos semestres que empiecen el mismo mes del mismo año
        UniqueConstraint("anio", "mesinicio", name="uq_semestre_anio_mesinicio"),
    )
