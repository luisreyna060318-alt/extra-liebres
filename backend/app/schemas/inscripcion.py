"""Esquemas de inscripciones y evaluaciones. Los de entrada y los de salida son distintos a propósito."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.alumno import normalizar_nocontrol

# Entero estricto de 0 a 100 (RN-05): 94.5, "90" o true no se aceptan
Calificacion = Annotated[int, Field(strict=True, ge=0, le=100, examples=[90])]


class InscripcionCrear(BaseModel):
    """Inscribir un alumno a un grupo (HU-05.1). Solo se manda el número de control."""

    # extra="forbid": un campo que no existe en el esquema se rechaza con 422 en lugar de ignorarse
    model_config = ConfigDict(extra="forbid")

    nocontrol: str = Field(min_length=1, examples=["19110001"])

    @field_validator("nocontrol")
    @classmethod
    def nocontrol_normalizado(cls, v: str) -> str:
        return normalizar_nocontrol(v)


class EvaluacionDatos(BaseModel):
    """Capturar o corregir la calificación (HU-05.2).

    El cliente NO manda el desempeño: lo calcula el servidor (RN-05). Por eso el esquema prohíbe campos
    extra: si alguien manda "desempenio" en el cuerpo, la API responde 422 y no guarda nada.
    """

    model_config = ConfigDict(extra="forbid")

    calificacion: Calificacion


class InscritoSalida(BaseModel):
    """Un alumno inscrito en un grupo, con su calificación y desempeño (nulos si aún no se evalúa)."""

    nocontrol: str
    alumno: str = Field(examples=["López García Ana"], description="Apellidos y nombre")
    carrera: str
    activo: bool = Field(description="false si el alumno fue dado de baja después de inscribirse")
    calificacion: int | None
    desempenio: str | None
