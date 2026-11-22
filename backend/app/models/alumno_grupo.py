from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constantes import DESEMPENOS
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.alumno import Alumno
    from app.models.grupo import Grupo


class AlumnoGrupo(Base):
    """Inscripción de un alumno en un grupo (relación N:M).

    Es una tabla con datos propios: guarda la calificación y el desempeño del alumno en ese grupo.
    Su llave primaria es compuesta (nocontrol, idgrupo): un alumno no se inscribe dos veces al mismo grupo.
    """

    __tablename__ = "alumno_grupo"

    nocontrol: Mapped[str] = mapped_column(
        ForeignKey("alumno.nocontrol", ondelete="RESTRICT"), primary_key=True
    )
    idgrupo: Mapped[int] = mapped_column(
        ForeignKey("grupo.idgrupo", ondelete="RESTRICT"), primary_key=True, index=True
    )
    # Nulos mientras el alumno no ha sido evaluado. El desempeño lo calcula el servidor (RN-05).
    calificacion: Mapped[int | None]
    desempenio: Mapped[str | None] = mapped_column(String(15))

    alumno: Mapped["Alumno"] = relationship(back_populates="inscripciones")
    grupo: Mapped["Grupo"] = relationship(back_populates="inscripciones")

    __table_args__ = (
        CheckConstraint("calificacion BETWEEN 0 AND 100", name="calificacion_valida"),
        CheckConstraint(f"desempenio IN {DESEMPENOS}", name="desempenio_valido"),
    )
