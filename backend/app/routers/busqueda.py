from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.constantes import ROLES_DE_PERSONAL
from app.core.deps import SesionDB, require_role
from app.schemas.busqueda import Busqueda
from app.services import busqueda_service

# La búsqueda es para administrador y capturista (muestra datos de alumnos): 401 sin sesión, 403 si es lector
router = APIRouter(
    prefix="/api/busqueda",
    tags=["Búsqueda"],
    dependencies=[Depends(require_role(*ROLES_DE_PERSONAL))],
    responses={
        401: {"description": "Sin sesión o sesión expirada"},
        403: {"description": "Los lectores no tienen acceso"},
    },
)


@router.get("", response_model=Busqueda, summary="Búsqueda global en alumnos y grupos")
def buscar(
    db: SesionDB,
    q: Annotated[str, Query(min_length=2, max_length=60, description="Texto a buscar (mínimo 2 letras)")],
):
    """Coincidencias en alumnos activos (nombre, apellidos o número de control) y en grupos (actividad, aula,
    día o promotor), agrupadas por tipo y con un máximo de 10 por tipo. Si nada coincide, las listas vienen vacías."""
    return busqueda_service.buscar(db, q)
