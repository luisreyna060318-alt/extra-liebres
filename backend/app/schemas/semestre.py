"""Esquemas de semestres (catálogo)."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.constantes import ANIO_SEMESTRE_MAXIMO, ANIO_SEMESTRE_MINIMO, PERIODOS_SEMESTRE


class SemestreDatos(BaseModel):
    anio: int = Field(ge=ANIO_SEMESTRE_MINIMO, le=ANIO_SEMESTRE_MAXIMO, examples=[2026])
    mesinicio: int = Field(ge=1, le=12, examples=[1], description="1 (enero) u 8 (agosto)")
    mestermino: int = Field(ge=1, le=12, examples=[6], description="6 si empieza en enero; 12 si empieza en agosto")

    @model_validator(mode="after")
    def periodo_valido(self):
        # Solo hay dos periodos: enero-junio y agosto-diciembre
        if (self.mesinicio, self.mestermino) not in PERIODOS_SEMESTRE:
            raise ValueError("El semestre debe ser de enero a junio o de agosto a diciembre")
        return self


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
