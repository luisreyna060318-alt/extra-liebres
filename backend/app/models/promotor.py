from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.grupo import Grupo


class Promotor(Base):
    """Responsable de impartir una actividad. Se identifica por su RFC (RN-01)."""

    __tablename__ = "promotor"

    rfc: Mapped[str] = mapped_column(String(13), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(60))
    apaterno: Mapped[str] = mapped_column(String(60))
    amaterno: Mapped[str | None] = mapped_column(String(60))
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())

    # Un promotor tiene muchos grupos (1:N)
    grupos: Mapped[list["Grupo"]] = relationship(back_populates="promotor")

    # El RFC de una persona física tiene 13 caracteres (12 en personas morales)
    __table_args__ = (CheckConstraint("length(rfc) BETWEEN 12 AND 13", name="rfc_valido"),)
