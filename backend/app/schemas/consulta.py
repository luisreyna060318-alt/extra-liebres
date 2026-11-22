"""Esquemas de las consultas transversales (HU-06.1). Solo hay salida: las consultas no modifican nada."""

from pydantic import BaseModel, Field


class InscritoConsulta(BaseModel):
    """Un renglón de la consulta de inscritos: el alumno, su grupo y cómo le fue."""

    nocontrol: str
    alumno: str = Field(examples=["López García Ana"], description="Apellidos y nombre")
    carrera: str
    idgrupo: int
    idextraescolar: int
    actividad: str = Field(examples=["Fútbol"])
    idsemestre: int
    semestre: str = Field(examples=["Enero-Junio 2026"])
    promotor: str
    calificacion: int | None
    desempenio: str | None
