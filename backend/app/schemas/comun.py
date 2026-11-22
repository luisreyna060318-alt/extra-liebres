from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Pagina(BaseModel, Generic[T]):
    """Respuesta de todos los listados: los elementos de la página y el total de toda la consulta."""

    items: list[T]
    total: int
    page: int
    size: int
