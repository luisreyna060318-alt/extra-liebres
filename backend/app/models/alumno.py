from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constantes import SEXOS
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.alumno_grupo import AlumnoGrupo


class Alumno(Base):
    """Alumno que cursó (o cursa) actividades extraescolares.

    Normalmente se da de baja (RN-02); solo se elimina si no tiene inscripciones."""

    __tablename__ = "alumno"

    # El número de control es texto, no número: puede tener ceros o letras al inicio (RN-01)
    nocontrol: Mapped[str] = mapped_column(String(15), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(60))
    apaterno: Mapped[str] = mapped_column(String(60))
    amaterno: Mapped[str | None] = mapped_column(String(60))
    sexo: Mapped[str] = mapped_column(String(1))
    carrera: Mapped[str] = mapped_column(String(80))
    campus: Mapped[str] = mapped_column(String(40))
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())

    # Un alumno tiene muchas inscripciones (relación N:M con grupo, a través de alumno_grupo)
    inscripciones: Mapped[list["AlumnoGrupo"]] = relationship(back_populates="alumno")

    __table_args__ = (CheckConstraint(f"sexo IN {SEXOS}", name="sexo_valido"),)
