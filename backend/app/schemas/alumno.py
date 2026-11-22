"""Esquemas de alumnos. Los de entrada (Crear/Actualizar) y el de salida son distintos a propósito."""

import re
from datetime import time
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from app.core.constantes import CARRERAS, SEXOS

# Textos que se limpian solos (espacios al inicio y al final) y no pueden quedar vacíos
Texto60 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=60)]
Texto80 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]
Texto40 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=40)]


class AlumnoDatos(BaseModel):
    """Datos que se capturan de un alumno (todo menos el número de control)."""

    nombre: Texto60 = Field(examples=["Ana"])
    apaterno: Texto60 = Field(examples=["López"])
    amaterno: Texto60 | None = Field(default=None, examples=["García"], description="Opcional")
    sexo: str = Field(examples=["F"], description="M o F")
    carrera: Texto80 = Field(examples=["ING. SISTEMAS COMPUTACIONALES"], description="Una de las carreras de la lista")
    campus: Texto40 = Field(examples=["Campus I"])

    @field_validator("amaterno", mode="before")
    @classmethod
    def amaterno_vacio_es_nulo(cls, v):
        # Un campo en blanco en el formulario significa "sin segundo apellido"
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @field_validator("sexo")
    @classmethod
    def sexo_valido(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in SEXOS:
            raise ValueError(f"El sexo debe ser uno de: {', '.join(SEXOS)}")
        return v

    @field_validator("carrera")
    @classmethod
    def carrera_valida(cls, v: str) -> str:
        # Se compara sin distinguir mayúsculas y se guarda con el nombre oficial: "ing. industrial" -> "ING. INDUSTRIAL"
        for oficial in CARRERAS:
            if v.upper() == oficial:
                return oficial
        raise ValueError("Elige una carrera de la lista")


def normalizar_nocontrol(valor: str) -> str:
    """Quita espacios y pone mayúsculas: 'b19110001 ' y 'B19110001' son el mismo número de control."""
    return valor.strip().upper()


class AlumnoCrear(AlumnoDatos):
    nocontrol: str = Field(examples=["19110001"], description="7 a 10 letras o números, sin espacios")

    @field_validator("nocontrol")
    @classmethod
    def nocontrol_valido(cls, v: str) -> str:
        v = normalizar_nocontrol(v)
        # Es texto, no número: puede empezar con ceros o con una letra (RN-01)
        if not re.fullmatch(r"[A-Z0-9]{7,10}", v):
            raise ValueError("El número de control debe tener de 7 a 10 letras o números, sin espacios")
        return v


class AlumnoActualizar(AlumnoDatos):
    """Edición de un alumno. El número de control no se puede cambiar (es su identificador)."""

    activo: bool | None = Field(
        default=None,
        description="Déjalo vacío para no cambiarlo. true reactiva a un alumno dado de baja.",
    )


class AlumnoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nocontrol: str
    nombre: str
    apaterno: str
    amaterno: str | None
    sexo: str
    carrera: str
    campus: str
    activo: bool


class OpcionesAlumno(BaseModel):
    """Valores para llenar los filtros y las listas desplegables.

    Las carreras son la lista fija; el campus, los que ya existen."""

    carreras: list[str]
    campus: list[str]


class HistorialItem(BaseModel):
    """Una actividad que cursó el alumno (HU-02.4)."""

    idgrupo: int
    actividad: str
    semestre_anio: int
    semestre_mesinicio: int
    semestre_mestermino: int
    promotor: str
    dia: str
    horainicio: time
    horatermino: time
    aula: str
    calificacion: int | None
    desempenio: str | None
