from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, String, false, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constantes import TIPOS_ACTIVIDAD
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.grupo import Grupo


class Extraescolar(Base):
    """Catálogo de actividades extraescolares (fútbol, danza, ajedrez...)."""

    __tablename__ = "extraescolar"

    idextraescolar: Mapped[int] = mapped_column(primary_key=True)
    nombreextra: Mapped[str] = mapped_column(String(80), unique=True)
    # El tipo decide qué campos pide el formulario de grupo (HU-04.2)
    tipo: Mapped[str] = mapped_column(String(20))
    # Si es al aire libre, el sistema muestra el pronóstico del clima (HU-08.1)
    al_aire_libre: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())

    grupos: Mapped[list["Grupo"]] = relationship(back_populates="extraescolar")

    __table_args__ = (CheckConstraint(f"tipo IN {TIPOS_ACTIVIDAD}", name="tipo_valido"),)
