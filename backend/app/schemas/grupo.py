"""Esquemas de grupos. Los de entrada (Crear/Actualizar) y el de salida son distintos a propósito."""

from datetime import time
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator, model_validator

from app.core.constantes import DIAS, DURACION_MINIMA_GRUPO_MINUTOS

Texto60 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=60)]


class GrupoDatos(BaseModel):
    """Datos que se capturan de un grupo.

    Crear y editar usan los mismos campos. Para el formulario dinámico (HU-04.2) basta con agregar aquí
    el campo nuevo (por ejemplo la instalación deportiva) y su validación; el servicio no cambia de forma.
    """

    idsemestre: int = Field(examples=[1])
    idextraescolar: int = Field(examples=[1])
    rfcpromotor: str = Field(examples=["RUSP800101AB1"], description="RFC del promotor")
    dia: str = Field(examples=["lunes"], description=f"Uno de: {', '.join(DIAS)}")
    horainicio: time = Field(examples=["08:00"])
    horatermino: time = Field(examples=["09:00"])
    aula: Texto60 = Field(examples=["Aula 5"], description="Aula o lugar donde se imparte")

    @field_validator("rfcpromotor")
    @classmethod
    def rfc_normalizado(cls, v: str) -> str:
        # El RFC se guarda en mayúsculas y sin espacios
        return v.strip().upper()

    @field_validator("dia")
    @classmethod
    def dia_valido(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in DIAS:
            raise ValueError(f"El día debe ser uno de: {', '.join(DIAS)}")
        return v

    @model_validator(mode="after")
    def horario_valido(self):
        # RN-03: la hora de término debe ser posterior a la de inicio (si no, FastAPI responde 422)
        if self.horatermino <= self.horainicio:
            raise ValueError("La hora de término debe ser posterior a la hora de inicio")
        fin = self.horatermino.hour * 60 + self.horatermino.minute
        inicio = self.horainicio.hour * 60 + self.horainicio.minute
        if fin - inicio < DURACION_MINIMA_GRUPO_MINUTOS:
            raise ValueError("La actividad debe durar al menos 1 hora")
        return self


class GrupoCrear(GrupoDatos):
    pass


class GrupoActualizar(GrupoDatos):
    """Edición de un grupo: se reemplazan todos sus datos y se vuelven a validar los cruces (HU-04.4)."""


class GrupoSalida(BaseModel):
    """Un grupo con los nombres de la actividad, el promotor y el semestre (no solo los ids)."""

    model_config = ConfigDict(from_attributes=True)

    idgrupo: int
    idsemestre: int
    semestre: str = Field(examples=["Enero-Junio 2026"])
    idextraescolar: int
    actividad: str = Field(examples=["Fútbol"])
    tipo_actividad: str = Field(examples=["deportiva"])
    rfcpromotor: str
    promotor: str = Field(examples=["Pedro Ruiz Soto"])
    dia: str
    horainicio: time
    horatermino: time
    aula: str
    inscritos: int = Field(description="Número de alumnos inscritos en el grupo")
