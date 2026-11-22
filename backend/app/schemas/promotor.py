"""Esquemas de promotores. Los de entrada (Crear/Actualizar) y el de salida son distintos a propósito."""

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.alumno import Texto60


def normalizar_rfc(valor: str) -> str:
    """Quita espacios y pone mayúsculas: 'aaaa000101aaa ' y 'AAAA000101AAA' son el mismo RFC."""
    return valor.strip().replace(" ", "").upper()


class PromotorDatos(BaseModel):
    """Datos que se capturan de un promotor (todo menos el RFC)."""

    nombre: Texto60 = Field(examples=["Pedro"])
    apaterno: Texto60 = Field(examples=["Ruiz"])
    amaterno: Texto60 | None = Field(default=None, examples=["Soto"], description="Opcional")

    @field_validator("amaterno", mode="before")
    @classmethod
    def amaterno_vacio_es_nulo(cls, v):
        # Un campo en blanco en el formulario significa "sin segundo apellido"
        if isinstance(v, str) and not v.strip():
            return None
        return v


class PromotorCrear(PromotorDatos):
    rfc: str = Field(examples=["RUSP800101AB1"], description="12 o 13 caracteres: letras, 6 dígitos y 3 de homoclave")

    @field_validator("rfc")
    @classmethod
    def rfc_valido(cls, v: str) -> str:
        v = normalizar_rfc(v)
        # 3 o 4 letras + fecha (6 dígitos) + homoclave (3): da 12 caracteres (moral) o 13 (física)
        if not re.fullmatch(r"[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}", v):
            raise ValueError("El RFC debe tener 12 o 13 caracteres con el formato oficial (ej. RUSP800101AB1)")
        return v


class PromotorActualizar(PromotorDatos):
    """Edición de un promotor. El RFC no se puede cambiar (es su identificador)."""

    activo: bool | None = Field(
        default=None,
        description="Déjalo vacío para no cambiarlo. false desactiva al promotor y true lo reactiva.",
    )


class PromotorSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rfc: str
    nombre: str
    apaterno: str
    amaterno: str | None
    activo: bool
