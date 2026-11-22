from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, func, true
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constantes import ROLES
from app.core.database import Base


class Usuario(Base):
    """Cuenta para entrar al sistema. Tiene un solo rol: administrador, capturista o lector (RN-06)."""

    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    correo: Mapped[str] = mapped_column(String(120), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))  # nunca la contraseña en claro
    rol: Mapped[str] = mapped_column(String(20), default="lector")
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (CheckConstraint(f"rol IN {ROLES}", name="rol_valido"),)
