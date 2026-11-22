from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constantes import DIAS
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.alumno_grupo import AlumnoGrupo
    from app.models.extraescolar import Extraescolar
    from app.models.promotor import Promotor
    from app.models.semestre import Semestre


class Grupo(Base):
    """Una actividad extraescolar en un semestre, con promotor, día, horario y lugar."""

    __tablename__ = "grupo"

    idgrupo: Mapped[int] = mapped_column(primary_key=True)
    dia: Mapped[str] = mapped_column(String(10))
    horainicio: Mapped[time]
    horatermino: Mapped[time]
    # Aula (cultural/cívica) o instalación deportiva (deportiva), según el tipo de actividad
    aula: Mapped[str] = mapped_column(String(60))

    # Llaves foráneas. ondelete="RESTRICT": no se puede borrar algo que tenga grupos (RN-08).
    idsemestre: Mapped[int] = mapped_column(
        ForeignKey("semestre.idsemestre", ondelete="RESTRICT"), index=True
    )
    idextraescolar: Mapped[int] = mapped_column(
        ForeignKey("extraescolar.idextraescolar", ondelete="RESTRICT"), index=True
    )
    rfcpromotor: Mapped[str] = mapped_column(
        ForeignKey("promotor.rfc", ondelete="RESTRICT"), index=True
    )

    semestre: Mapped["Semestre"] = relationship(back_populates="grupos")
    extraescolar: Mapped["Extraescolar"] = relationship(back_populates="grupos")
    promotor: Mapped["Promotor"] = relationship(back_populates="grupos")
    inscripciones: Mapped[list["AlumnoGrupo"]] = relationship(back_populates="grupo")

    __table_args__ = (
        CheckConstraint(f"dia IN {DIAS}", name="dia_valido"),
        # RN-03: la hora de inicio debe ser anterior a la de término
        CheckConstraint("horainicio < horatermino", name="horario_valido"),
    )
