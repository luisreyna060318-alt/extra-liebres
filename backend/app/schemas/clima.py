from pydantic import BaseModel


class ClimaSalida(BaseModel):
    """Si `disponible` es false solo viene `mensaje`; si es true vienen los demás campos."""

    disponible: bool
    mensaje: str | None = None
    temperatura: float | None = None  # °C
    prob_lluvia: int | None = None  # % máximo de las próximas 12 horas
    aviso_lluvia: bool | None = None
