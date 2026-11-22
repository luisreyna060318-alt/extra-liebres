from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.deps import SesionDB, get_current_user
from app.schemas.dashboard import ResumenSalida
from app.services import dashboard_service

# Sesión requerida (administrador o capturista): 401 si no hay
router = APIRouter(
    prefix="/api/dashboard",
    tags=["Tablero"],
    dependencies=[Depends(get_current_user)],
    responses={401: {"description": "Sin sesión o sesión expirada"}},
)


@router.get(
    "/resumen",
    response_model=ResumenSalida,
    summary="Cifras del tablero de un semestre",
    responses={404: {"description": "El semestre no existe"}},
)
def resumen(
    db: SesionDB,
    semestre: Annotated[int | None, Query(description="Id del semestre; si se omite, el más reciente")] = None,
):
    """Totales, inscritos por actividad, distribución por desempeño y promedio de calificación del semestre.

    `alumnos_activos` es global; lo demás se calcula sobre el semestre elegido."""
    return dashboard_service.obtener_resumen(db, semestre)
