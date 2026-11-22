from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.deps import SesionDB, get_current_user
from app.core.paginacion import Paginacion
from app.schemas.comun import Pagina
from app.schemas.consulta import InscritoConsulta
from app.services import consulta_service

# Las consultas exigen sesión (administrador o capturista): 401 si no hay
router = APIRouter(
    prefix="/api/consultas",
    tags=["Consultas"],
    dependencies=[Depends(get_current_user)],
    responses={401: {"description": "Sin sesión o sesión expirada"}},
)


@router.get("/inscritos", response_model=Pagina[InscritoConsulta], summary="Alumnos inscritos por actividad y semestre")
def inscritos(
    db: SesionDB,
    paginacion: Annotated[Paginacion, Depends()],
    extraescolar: Annotated[int | None, Query(description="id de la actividad")] = None,
    semestre: Annotated[int | None, Query(description="id del semestre")] = None,
):
    """Alumnos inscritos con su grupo, calificación y desempeño. Filtros opcionales y paginación
    (10 por página por defecto). Si nada cumple, `items` viene vacío y `total` en 0."""
    filas, total = consulta_service.inscritos(db, paginacion, extraescolar, semestre)
    return Pagina[InscritoConsulta](items=filas, total=total, page=paginacion.page, size=paginacion.size)
