"""Esquemas de semestres (catálogo)."""

from pydantic import BaseModel, ConfigDict, Field


class SemestreDatos(BaseModel):
    anio: int = Field(ge=2000, le=2100, examples=[2026])
    mesinicio: int = Field(ge=1, le=12, examples=[1], description="Mes de inicio (1 a 12)")
    mestermino: int = Field(ge=1, le=12, examples=[6], description="Mes de término (1 a 12)")


class SemestreCrear(SemestreDatos):
    pass


class SemestreActualizar(SemestreDatos):
    pass


class SemestreSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idsemestre: int
    anio: int
    mesinicio: int
    mestermino: int
