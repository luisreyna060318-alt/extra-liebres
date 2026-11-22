"""Esquemas de la búsqueda global (HU-06.2). Solo hay salida: buscar no modifica nada."""

from pydantic import BaseModel, Field


class AlumnoCoincidencia(BaseModel):
    nocontrol: str
    alumno: str = Field(examples=["López García Ana"], description="Apellidos y nombre")
    carrera: str


class GrupoCoincidencia(BaseModel):
    idgrupo: int
    descripcion: str = Field(examples=["Fútbol (grupo 3), lunes de 08:00 a 09:00"])
    semestre: str = Field(examples=["Enero-Junio 2026"])
    promotor: str


class Busqueda(BaseModel):
    """Coincidencias agrupadas por tipo. Cada tipo trae como máximo 10; `*_hay_mas` avisa si hubo más."""

    q: str
    alumnos: list[AlumnoCoincidencia]
    alumnos_hay_mas: bool
    grupos: list[GrupoCoincidencia]
    grupos_hay_mas: bool
