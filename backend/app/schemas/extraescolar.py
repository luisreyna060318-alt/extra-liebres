"""Esquemas de actividades extraescolares (catálogo)."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constantes import TIPOS_ACTIVIDAD
from app.schemas.alumno import Texto80


class ExtraescolarDatos(BaseModel):
    nombreextra: Texto80 = Field(examples=["Fútbol"], description="Único (sin distinguir mayúsculas)")
    tipo: str = Field(examples=["deportiva"], description="deportiva, cultural o civica")
    al_aire_libre: bool = Field(default=False, description="Si es true, se mostrará el pronóstico del clima")

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in TIPOS_ACTIVIDAD:
            raise ValueError(f"El tipo debe ser uno de: {', '.join(TIPOS_ACTIVIDAD)}")
        return v


class ExtraescolarCrear(ExtraescolarDatos):
    pass


class ExtraescolarActualizar(ExtraescolarDatos):
    activo: bool | None = Field(
        default=None,
        description="Déjalo vacío para no cambiarlo. false desactiva la actividad y true la reactiva.",
    )


class ExtraescolarSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idextraescolar: int
    nombreextra: str
    tipo: str
    al_aire_libre: bool
    activo: bool
