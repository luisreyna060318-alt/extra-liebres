"""Paginación común a todos los listados (RN-11): ?page=1&size=10."""

from fastapi import Query


class Paginacion:
    """Dependencia de FastAPI: lee page y size de la URL y valida sus límites."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Número de página (empieza en 1)"),
        size: int = Query(10, ge=1, le=50, description="Elementos por página (máximo 50)"),
    ):
        self.page = page
        self.size = size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size
