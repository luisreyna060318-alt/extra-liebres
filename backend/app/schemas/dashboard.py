"""Esquemas de salida del tablero de resumen (HU-07.1)."""

from pydantic import BaseModel


class Totales(BaseModel):
    alumnos_activos: int  # global: no depende del semestre
    grupos: int
    inscripciones: int


class InscritosPorActividad(BaseModel):
    actividad: str
    total: int


class DistribucionDesempenio(BaseModel):
    desempenio: str
    total: int


class ResumenSalida(BaseModel):
    totales: Totales
    inscritos_por_actividad: list[InscritosPorActividad]
    distribucion_desempenio: list[DistribucionDesempenio]
    # None cuando no hay ninguna inscripción calificada (no se divide entre cero)
    promedio_calificacion: float | None
